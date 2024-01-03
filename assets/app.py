import yaml
from flask import Flask, jsonify
from flask_restful import Resource, Api
from munch import munchify, unmunchify
from downloader import Downloader, queue
import db
import asyncio

with open('./config.yaml') as stream:
    try:
        yamlfile = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
config = munchify(yamlfile)

app = Flask(__name__)
api = Api(app)
youtube = Downloader()

class Download(Resource):
  def __init__(self):
      self.database = db.Database()

  async def get(self, url):
    try:
      self.database.new_queue(downloaded=False, url=url)
      await queue.start
      return {'message': 'Download request received and queued'}
    except Exception as e:
      return {'message': f'Error: {e}'}
    

class DownloadInfo(Resource):
    def get(self):
        data = youtube.getjson()
        data = unmunchify(data)
        return jsonify(data)

class Ping(Resource):
    def get(self):
        return {'ping': 'pong'}

api.add_resource(Download, '/download/<string:url>')
api.add_resource(Ping, '/ping')
api.add_resource(DownloadInfo, '/getjson')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=config.port)
