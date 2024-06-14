import yt_dlp
from munch import munchify
from typing import Optional
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from pytube import Playlist
import asyncio
import sys
from time import sleep
from config import config

from queue import Empty, Queue
try:
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

  debug_init(False, False)

  if __name__ != '__main__':
    try:
      from db import Database
      db = Database()
    except ImportError:
      try: 
        from .db import Database
        db = Database()
      except:
        logger.error('Failed to import db')
        exit()
  else:
    logger.warning("Didn't try to import db")
    pass


  class MyLogger:
      def debug(self, msg):
          # For compatibility with youtube-dl, both debug and info are passed into debug
          # You can distinguish them by the prefix '[debug] '
          if msg.startswith('[debug] '):
              logger.debug(msg)
          else:
              self.info(msg)

      def info(self, msg):
          pass

      def warning(self, msg):
          pass

      def error(self, msg):
        print(msg)
        pass

  class Downloader:
    debug_init(True, False)
    wait = False
    StatusStarted=False
    Started=False
    host=None
    port=None
    download_path=None
    Status=None
    filename=None
    time_elapse=None
    percent=None
    eta=None
    url=None
    title=None
    playlist_url=None
    PostProcessorStarted=None
    PlaylistTitle=None
    downloading=False


    
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=1)
    loop.set_default_executor(executor)


    def __init__(
      self, host:Optional[str]=None, 
      download_path:Optional[str]='downloads/', 
      port:Optional[int]=5000,
    ):
      self.db = Database()
      if not host == None:
        self.host = host
        self.port = port
        self.download_path = download_path

    def progress_hook(self, d):
      d = munchify(d)
      
      if d.status == 'error':
        pass

      if d.status == 'finished':
        logger.trace(f'Done Downloading "{d["filename"]}"')
        self.StatusStarted = False
        self.filename = d['filename']
        self.time_elapse = d['elapsed']
        self.PostProcessorStarted=False
        
      if d.status == 'downloading':
        if not self.StatusStarted:
          logger.trace(f'Now Downloading "{d["filename"]}"')
          self.StatusStarted = True

        self.filename = d['filename']
        self.percent = d['_percent_str']
        self.eta = d['_eta_str']
        self.speed = d['speed']

    def postprocessor_hooks(self, d):
      
      d = munchify(d)
      if d.status == 'started':
        info = munchify(d['info_dict'])
        self.url = info.webpage_url
        self.title = info.title
        self.download_path = info.filepath 
        self.Status = 'Started'
        pass
      if d.status == 'finished': 
        logger.trace('PostProcessor Hook finished')
        if not self.PostProcessorStarted:
          self.db.mark_video_downloaded(playlist_url=self.playlist_url, url=self.url, title=self.title, download_path=self.download_path, elapsed=self.time_elapse)
          self.PostProcessorStarted =True
        self.Status = 'Finished'
        pass

    def ydl_opts(self):
      ydl_opts = {
        'ratelimit': config.ratelimit, # Kilobytes
        'logger': MyLogger(),
        'breakonexisting': True,
        'progress_hooks': [self.progress_hook],
        'postprocessor_hooks': [self.postprocessor_hooks],
        'writethumbnail': True,
        'outtmpl': 'downloads/%(playlist_title)s/%(playlist_autonumber)s - %(title)s.%(ext)s',
        'skip_broken': True,
        'ignoreerrors': True,
        'postprocessors': [
        {'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': 'None'},
        {'add_metadata': 'True', 'key': 'FFmpegMetadata'},
        {'already_have_thumbnail': False, 'key': 'EmbedThumbnail'}
      ]}
      return ydl_opts

    def playlist_title_opts(self):
      ydl_opts = {
        'quiet': True,
        'extract_flat': True
      }
      return ydl_opts
    

    def download_thread(self, url):
      """ url is the YT url for download """
      try:
        logger.info(f'begin download for {url}')
        logger.trace('Start for loop')
        with yt_dlp.YoutubeDL(self.playlist_title()) as ydl:
          result = ydl.extract_info(url, download=False)
          if result is not None:
            title_url = result['url']
            playlist = Playlist(title_url)
            logger.trace(f'Playlist: {playlist}')
            self.PlaylistTitle = playlist.title
          else:
            logger.error(f"Couldn't extract info for URL: {url}")
        with yt_dlp.YoutubeDL(self.ydl_opts()) as ydl:
          self.playlist_url=url
          ydl.download(url)
          self.db.mark_playlist_downloaded(url, self.PlaylistTitle)
      except Exception as e:
        logger.error(e)
        

    def getjson(self):
      data = {
        'info': {
        'Download_path': self.download_path,
        'filename': self.filename,
        'time_elapse': self.time_elapse,
        'percent': self.percent,
        'eta': self.eta
        },
      }
      return data


except Exception as e:
  logger.error(e)