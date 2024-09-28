from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException,  Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import jwt

from pydantic import BaseModel

from datetime import timedelta, datetime

from functools import wraps
import tracemalloc
from time import perf_counter


from munch import unmunchify
from loguru import logger

from sys import stderr

import utils


# Use a strong secret key
SECRET_KEY = "d7fe6bb7e5a7277930129997d82d84e8024d336013ceeb09877129c506913552"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def debug_init(trace, debug):
    logger.remove()
    if debug:
        logger.add(stderr, level='DEBUG')
    elif trace:
        logger.add(stderr, level='TRACE')
    else:
        logger.add(stderr, level='INFO')
        pass
    pass


Database_con: bool = False

DatabaseConFailures: int = 0


class Token(BaseModel):
    access_token: str
    token_type: str


shared_data = {
    'info': {
        'Download_path': None,
        'filename': None,
        'time_elapse': None,
        'percent': None,
        'eta': None
    },
}


def check_database_con(func):
    async def wrapper(*args, **kwargs):
        check = utils.interaction.check_conn()
        if check['conn']:
            result = await func(*args, **kwargs)
            return result
        else:
            logger.error(
                '''There Was A problem connecting to database! Ensure the server is running and your Credentials are correct! If That doesn't work Run server in debug mode!''')
            logger.error(check)
            return "There Was A problem connecting to database! Ensure the server is running and your Credentials are correct! If That doesn't work Run server in debug mode!"
    return wrapper


def performance(func):
    async def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = perf_counter()
        await func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        finish_time = perf_counter()
        logger.trace(f'Function: {func.__name__}')
        logger.trace(f'Method: {func.__doc__}')
        logger.trace(f'Memory usage:\t\t {current / 10**6:.6f} MB \n'
                     f'Peak memory usage:\t {peak / 10**6:.6f} MB ')
        logger.trace(f'Time elapsed is seconds: {
                     finish_time - start_time:.6f}')
        logger.trace(f'{"-"*40}')
        tracemalloc.stop()
    return wrapper


@check_database_con
@performance
async def scanDatabase():
    return utils.interaction.fetchNextItem()


@asynccontextmanager
async def lifespan(app: FastAPI):
    debug_init(True, True)
    utils.interaction.create_tables()
    scheduler = AsyncIOScheduler()
    # Check and fetch next database item Every 5 seconds
    scheduler.add_job(scanDatabase, 'interval', seconds=5)
    scheduler.start()
    yield

    print('Shutting down...')
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@check_database_con
@performance
@app.post('/download/{url}/')
async def download_route(url: str, token: str = Depends(oauth2_scheme)):
    """Attempts to add url to database for download"""
    return utils.interaction.createEntry(url)


@check_database_con
@performance
@app.get('/ping')
async def ping():
    """Ping the server and respond in kind"""
    return {'ping': 'pong'}


# Make use authentication
@check_database_con
@performance
@app.get('/getjson')
async def get_json(token: str = Depends(oauth2_scheme)):
    """Get current downloading information"""
    # data = youtube.getjson()
    data = unmunchify(shared_data)
    return JSONResponse(content=data)


class User(BaseModel):
    username: str
    password: str


@check_database_con
@performance
@app.post('/register')
async def register(user: User, token: str = Depends(oauth2_scheme)):
    data = utils.interaction.new_user(user.username, user.password)
    data.password = "Hidden For Security"  # type: ignore
    data.salt = "Hidden For Security"  # type: ignore
    return data


@check_database_con
@performance
@app.post("/login", response_model=Token)
async def login(req: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    verif, user = utils.interaction.verify_user(
        form_data.username, form_data.password)
    if not verif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
