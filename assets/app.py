from flask import Flask, jsonify, request 
from flask_restful import Resource, Api
from downloader import Downloader
import threading

app = Flask(__name__) 
api = Api(app) 
youtube = Downloader(server=True)
class Download(Resource):

  def get(self, url):
    t1 = threading.Thread(target=youtube.download, args=(url,))
    t1.start()
    # return youtube.json()
    return {'message': 'Download started asynchronously'}
  
  
api.add_resource(Download, '/download/<string:url>')


if __name__ == '__main__': 
    app.run(debug = True) 