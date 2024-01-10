import yaml
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from munch import munchify, unmunchify
from downloader import Downloader, queue
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import db
from loguru import logger
import sys

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

debug_init(True, False)

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


with open('./config.yaml') as stream:
  try:
    yamlfile = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)
config = munchify(yamlfile)

app = FastAPI(debug=True)
youtube = Downloader()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
  username: str
  email: str | None = None
  full_name: str | None = None
  disabled: bool | None = None

def fake_decode_token(token):
  return User(
    username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
  )

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class Download:
  def __init__(self):
    self.database = db.Database()

  async def download(self, url):
    logger.trace('Download route got')
    data = db.Database()
    logger.trace('create db.Database instance')
    data.db_create()
    logger.trace('Create tables')
    try:
      
      logger.trace('new queue')
      self.database.new_queue(url=url)
      
      logger.trace('init queue instance')
      q = queue()
      logger.trace('queue.fill')
      self.myqueue = await q.fill()
      queue_list = []
      logger.trace('fill queue_list dict')
      for queue_item in self.myqueue:
        queue_list.append(queue_item.url)
      logger.debug(queue_list)
      logger.trace('youtube.queue_dl')
      await youtube.queue_dl(queue_list)
      
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



download = Download()
favicon_path = 'assets/favicon.ico'

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
  return FileResponse(favicon_path)

@app.get('/download/{url}')
#?  add this to download_route function to enable token authentication", token: Annotated[str, Depends(oauth2_scheme)]"
async def download_route(url: str):
  return await download.download(url)

@app.get('/ping')
async def ping():
  return {'ping': 'pong'}

@app.get('/getjson')
async def get_json():
  data = youtube.getjson()
  data = unmunchify(data)
  return JSONResponse(content=data)


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

class UserInDB(User):
    hashed_password: str

def fake_hash_password(password: str):
    return "fakehashed" + password

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}




if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=config.port)