import threading

import yaml
from flask import Flask, jsonify
from flask_restful import Resource, Api
from munch import munchify, unmunchify
import db
from downloader import Downloader

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
  db.database()
  




class DownloadInfo(Resource):
  def get(self):
    data = youtube.getjson()
    data = unmunchify(data)
    return jsonify(data)


class ping(Resource):
  def get(self):
    
    return {
      'ping': 'pong',
            }


api.add_resource(Download, '/download/<string:url>')
api.add_resource(ping, '/ping')
api.add_resource(DownloadInfo, '/getjson')


if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=config.port)

