import secrets
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sys


from typing import Annotated

from loguru import logger
from munch import munchify, unmunchify
import yaml

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials


from sqlalchemy.exc import IntegrityError

from downloader import Downloader, queue
import db



from queue import Queue


def debug_init(trace, debug):
    logger.remove()
    if debug:
        logger.add(sys.stderr, level='DEBUG')
    elif trace:
        logger.add(sys.stderr, level='TRACE')
    else:
        logger.add(sys.stderr, level='INFO')
        pass
    pass



with open('./config.yaml') as stream:
  try:
    yamlfile = yaml.safe_load(stream)
    config = munchify(yamlfile)
  except yaml.YAMLError as exc:
    print(exc)
    raise ValueError("Please check your config file!")

debug_init(config.debug, config.debug)

app = FastAPI(debug=config.debug)
security = HTTPBasic()

youtube = Downloader()


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(config.username, 'utf-8') # type: ignore
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(config.password, 'utf-8') # type: ignore
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class Download:
  def __init__(self, download_queue):
    self.database = db.Database()
    self.database.db_create()
    self.dlq = download_queue


  async def download(self, url):
    logger.trace('Download route got')
    logger.trace('create db.Database instance')
    logger.trace('Create tables')
    try:
      
      logger.trace('new queue')
      self.database.new_queue(url=url)
      
      logger.trace('init queue instance')
      self.dlq.put(url)
      
      return {'message': 'Download request received and queued',
              'error': None}
      
    except IntegrityError as e:
      return {
        'message': f'Duplicate Entry. Link already exists!',
        'error': e
        }
    except HTTPException as e:
      return {
        'message': f' HTTPException',
        'error': e
        }
    except Exception as e:
      print(e)
      return {
      'message': f'An Error Occured', 
      'error': e
        }


download_queue = Queue()
download = Download(download_queue)


@app.get("/users/me")
def read_current_user(username: Annotated[str, Depends(get_current_username)]):
    return {"username": username}

@app.get('/download/{url}')
async def download_route(username: Annotated[str, Depends(get_current_username)], url: str):
  return await download.download(url)

@app.get('/ping')
async def ping():
  return {'ping': 'pong'}

@app.get('/getjson')
async def get_json(username: Annotated[str, Depends(get_current_username)]):
  data = youtube.getjson()
  data = unmunchify(data)
  return JSONResponse(content=data)


def run_uvicorn():
  uvicorn.run(app, host='0.0.0.0', port=config.port)

def run_asyncio():
  asyncio.run(youtube.queue_dl(dlq=download_queue))

if __name__ == '__main__':
  import uvicorn
  
  with ThreadPoolExecutor(max_workers=2) as executor:
      future1 = executor.submit(run_asyncio)
      future2 = executor.submit(run_uvicorn)
