import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from munch import munchify, unmunchify
from downloader import Downloader, queue
from sqlalchemy.exc import IntegrityError
import db

with open('./config.yaml') as stream:
    try:
        yamlfile = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
config = munchify(yamlfile)

app = FastAPI(debug=True)
youtube = Downloader()

class Download:
    def __init__(self):
        self.database = db.Database()

    async def download(self, url):
        data = db.Database()
        await data.db_create()
        try:
          
          await self.database.new_queue(downloaded=False, url=url)
          
          q = queue()
          self.myqueue = await q.fill()
          queue_list = {}
          for queue_item in self.myqueue:
            queue_list[queue_item.id] = queue_item.url
          print(queue_list)          
          
          return {'message': 'Download request received and queued'}
        except IntegrityError as e:
          return {
            'message': f'Duplicate Entry. Link already exists!',
            'error': e
            }
        except HTTPException as e:
          return {
            'message': f'HTTPException: {e}',
            'error': e
            }
        except Exception as e:
            return {
            'message': f'An Error Occured',
            'error': e
            }

download = Download()

@app.get('/download/{url}')
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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=config.port)