from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from munch import unmunchify
from downloader import Downloader, queue

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

async def run_blocking_function(func):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func)

async def scanDatabase_async():
    await run_blocking_function()


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(scanDatabase_async())
    yield
    print('Shutting down...')

app = FastAPI(lifespan=lifespan)
youtube=Downloader()



#! Make use authentication
@app.get('/download/{dltype}/{url}/')
async def download_route(dltype:str,  url: str):
  if dltype not in ['audio', 'video']:
    return {
      'message': f'An Error Occured', 
      'error': 'Incorrect DlType!'
        }
  return await download.download(url=url, vidtype=dltype)

@app.get('/ping')
async def ping():
  return {'ping': 'pong'}

#! Make use authentication
@app.get('/getjson')
async def get_json():
  data = youtube.getjson()
  data = unmunchify(data)
  return JSONResponse(content=data)


