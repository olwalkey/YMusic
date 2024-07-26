from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from concurrent.futures import ThreadPoolExecutor

from datetime import datetime

from time import sleep
from munch import unmunchify

from sqlalchemy.orm import Session

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from assets import *



shared_data = {
  'info': {
  'Download_path': None,
  'filename': None,
  'time_elapse': None,
  'percent': None,
  'eta': None
  },
}



executor = ThreadPoolExecutor(max_workers=1)

def scanDatabase():
    pass

def tick():
  print('Tick! The time is: %s' % datetime.now())

@asynccontextmanager
async def lifespan(app: FastAPI):

    scheduler=AsyncIOScheduler()
    scheduler.add_job(tick, 'interval', seconds=1)
    scheduler.start()
    yield
    print('Shutting down...')

app = FastAPI(lifespan=lifespan)

oath2_scheme = OAuth2PasswordBearer(tokenUrl="Token")

origins = [
   'http://localhost:3000',
   'https://youtube.zima.ashbyte.com'
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

#! Make use authentication
@app.post('/download/{dltype}/{url}/')
async def download_route(dltype:str,  url: str):
  if dltype not in ['audio', 'video']:
    return {
      'message': f'An Error Occured', 
      'error': 'Incorrect DlType!'
        }
  # return await download.download(url=url, vidtype=dltype)

@app.get('/ping')
async def ping():
  return {'ping': 'pong'}

#! Make use authentication
@app.get('/getjson')
async def get_json():
  # data = youtube.getjson()
  data = unmunchify(data)
  return JSONResponse(content=data)




















#? Progress Hooks

    # def progress_hook(self, d):
    #   d = munchify(d)
      
    #   if d.status == 'error':
    #     pass

    #   if d.status == 'finished':
    #     logger.trace(f'Done Downloading "{d["filename"]}"')
    #     self.StatusStarted = False
    #     self.filename = d['filename']
    #     self.time_elapse = d['elapsed']
    #     self.PostProcessorStarted=False
        
    #   if d.status == 'downloading':
    #     if not self.StatusStarted:
    #       logger.trace(f'Now Downloading "{d["filename"]}"')
    #       self.StatusStarted = True

    #     self.filename = d['filename']
    #     self.percent = d['_percent_str']
    #     self.eta = d['_eta_str']
    #     self.speed = d['speed']

    # def postprocessor_hooks(self, d):

#? Downloader Options

    # def ydl_opts(self):
    #   ydl_opts = {
    #     'ratelimit': config.ratelimit, # Kilobytes
    #     'logger': MyLogger(),
    #     'breakonexisting': True,
    #     'progress_hooks': [self.progress_hook],
    #     'postprocessor_hooks': [self.postprocessor_hooks],
    #     'writethumbnail': True,
    #     'outtmpl': 'downloads/%(playlist_title)s/%(playlist_autonumber)s - %(title)s.%(ext)s',
    #     'skip_broken': True,
    #     'ignoreerrors': True,
    #     'postprocessors': [
    #     {'key': 'FFmpegExtractAudio',
    #       'preferredcodec': 'mp3',
    #       'preferredquality': 'None'},
    #     {'add_metadata': 'True', 'key': 'FFmpegMetadata'},
    #     {'already_have_thumbnail': False, 'key': 'EmbedThumbnail'}
    #   ]}
    #   return ydl_opts

    # def playlist_title_opts(self):
    #   ydl_opts = {
    #     'quiet': True,
    #     'extract_flat': True
    #   }
    #   return ydl_opts