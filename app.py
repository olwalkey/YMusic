from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from time import time

from datetime import datetime

from munch import unmunchify
from loguru import logger

from sys import stderr

import utils


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


Database_con = False

shared_data = {
    'info': {
        'Download_path': None,
        'filename': None,
        'time_elapse': None,
        'percent': None,
        'eta': None
    },
}


def scanDatabase():
    pass


def tick():
    print('Tick! The time is: %s' % datetime.now())


@asynccontextmanager
async def lifespan(app: FastAPI):
    debug_init(True, False)
    yield
    print('Shutting down...')

app = FastAPI(lifespan=lifespan)

oath2_scheme = OAuth2PasswordBearer(tokenUrl="Token")

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


def check_database_con(func):
    async def wrapper(*args, **kwargs):
        if Database_con:
            result = func(*args, **kwargs)
        else:
            logger.error(
                '''There Was A problem connecting to database! Ensure the server is running and your Credentials are correct! If That doesn't work Run server in debug mode!''')
            return "There was A problem connecting to the database! Please check server logs"
        return result
    return wrapper


def time_function(func):
    async def wrapper(*args, **kwargs):
        start = time()
        func(*args, **kwargs)
        end = time()
        logger.trace(f'{func.name} Took {end-start} To Execute')


# def get_db():
#    db=SessionLocal

# Make use authentication
@check_database_con
@time_function
@app.post('/download/{url}/')
async def download_route(url: str):
    return utils.youtube.start_download(url=url)


@check_database_con
@time_function
@app.get('/ping')
async def ping():
    return {'ping': 'pong'}


# Make use authentication
@check_database_con
@time_function
@app.get('/getjson')
async def get_json():
    # data = youtube.getjson()
    data = unmunchify(shared_data)
    return JSONResponse(content=data)
