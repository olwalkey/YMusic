from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler

from functools import wraps
import tracemalloc
from time import perf_counter


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


Database_con: bool = False

DatabaseConFailures: int = 0

shared_data = {
    'info': {
        'Download_path': None,
        'filename': None,
        'time_elapse': None,
        'percent': None,
        'eta': None
    },
}


def check_database_con(DatabaseConFailures):
    def check_database_con(func):
        async def wrapper(*args, **kwargs):
            if Database_con:
                result = func(*args, **kwargs)
                return result
            else:
                logger.error(
                    '''There Was A problem connecting to database! Ensure the server is running and your Credentials are correct! If That doesn't work Run server in debug mode!''')
                DatabaseConFailures += 1
                print(DatabaseConFailures)

                return False
        return wrapper
    return check_database_con


def performance(func):
    async def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = perf_counter()
        func(*args, **kwargs)
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


@check_database_con
@performance
async def scanDatabase():
    fetched = utils.interaction.fetchNextItem()

    if not fetched:
        return "There was A problem connecting to the database! Please check server logs"
    else:


@asynccontextmanager
async def lifespan(app: FastAPI):
    debug_init(True, False)
    scheduler = BackgroundScheduler()
    # Check and fetch next database item
    scheduler.add_job(scanDatabase, 'interval', seconds=5)
    scheduler.start()
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


# def get_db():
#    db=SessionLocal

# Make use authentication
@check_database_con(DatabaseConFailures)
@performance
@app.post('/download/{url}/')
async def download_route(url: str):
    """Request A Download from the Database"""
    return utils.youtube.start_download(url=url)


@check_database_con(DatabaseConFailures)
@performance
@app.get('/ping')
async def ping():
    """Ping the server and respond in kind"""
    return {'ping': 'pong'}


# Make use authentication
@check_database_con(DatabaseConFailures)
@performance
@app.get('/getjson')
async def get_json():
    """Get current downloading information"""
    # data = youtube.getjson()
    data = unmunchify(shared_data)
    return JSONResponse(content=data)
