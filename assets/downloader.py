import yt_dlp
from munch import munchify
from typing import Optional
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from pytube import Playlist
import asyncio
import sys
from time import sleep
from .config import config

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
        exit()
  else:
    pass


  class MyLogger:
      def debug(self, msg):
          # For compatibility with youtube-dl, both debug and info are passed into debug
          # You can distinguish them by the prefix '[debug] '
          if msg.startswith('[debug] '):
              pass
          else:
              self.info(msg)

      def info(self, msg):
          pass

      def warning(self, msg):
          pass

      def error(self, msg):
        print(msg)
        pass


  class queue:
    started=False

    def __init__(self):
      self.db = db
      
    def fill(self):
      """returns all non downloaded items in the database

      Returns:
          dict: id: url
      """
      self.myqueue = self.db.QueueNotDone()
      return self.myqueue

  def format_selector(ctx):
      """ Select the best video and the best audio that won't result in an mkv.
      NOTE: This is just an example and does not handle all cases """

      formats = ctx.get('formats')[::-1]

      # acodec='none' means there is no audio
      best_video = next(f for f in formats
                        if f['vcodec'] != 'none' and f['acodec'] == 'none')

      # find compatible audio extension
      audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
      # vcodec='none' means there is no video
      best_audio = next(f for f in formats if (
          f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

      # These are the minimum required fields for a merged format
      yield {
          'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
          'ext': best_video['ext'],
          'requested_formats': [best_video, best_audio],
          # Must be + separated list of protocols
          'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
      }

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

    urls=[]

    
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
      
      if d.status == 'error':   #type: ignore
        pass    #type: ignore
          #type: ignore
      if d.status == 'finished':    #type: ignore
        logger.trace(f'Done Downloading "{d["filename"]}"')   #type: ignore
        self.StatusStarted = False    #type: ignore
        self.filename = d['filename']   #type: ignore
        self.time_elapse = d['elapsed']   #type: ignore
        self.PostProcessorStarted=False   #type: ignore
        
      if d.status == 'downloading':   #type: ignore
        if not self.StatusStarted:    #type: ignore
          logger.trace(f'Now Downloading "{d["tmpfilename"]}"')       #type: ignore
          self.StatusStarted = True   #type: ignore

        self.filename = d['tmpfilename']    #type: ignore
        self.percent = d['_percent_str']    #type: ignore
        self.eta = d['_eta_str']    #type: ignore

    def postprocessor_hooks(self, d):   #type: ignore
      d = munchify(d)   #type: ignore
      if d.status == 'started':   #type: ignore
        info = munchify(d['info_dict'])   #type: ignore
        self.url = info.webpage_url   #type: ignore
        self.title = info.title   #type: ignore
        self.download_path = info.filepath    #type: ignore
        self.Status = 'Started'   #type: ignore
        pass
      if d.status == 'finished':    #type: ignore
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
    
    def video_opts(self):
      ydl_opts = {
        # 'ratelimit': 500000, # Kilobytes
        'logger': MyLogger(),
        'breakonexisting': True,
        'progress_hooks': [self.progress_hook],
        'postprocessor_hooks': [self.postprocessor_hooks],
        'writethumbnail': True,
        'outtmpl': 'videos/%(playlist_title)s/%(playlist_autonumber)s - %(title)s.%(ext)s',
        'skip_broken': True,
        'ignoreerrors': True,
        'format': format_selector,
        'postprocessors': [
        {'add_metadata': 'True', 'key': 'FFmpegMetadata'},
        {'already_have_thumbnail': False, 'key': 'EmbedThumbnail'}
      ]}
      return ydl_opts

    def playlist_title(self):
      ydl_opts = {
        'quiet': True,
        'extract_flat': True
      }
      return ydl_opts
    
    async def queue_dl(self, dlq: Queue, Shutdown = False, qurls: Optional[list] = None):
      logger.trace(f'Started: {self.Started}')
      logger.debug(qurls)

      for x in self.db.QueueNotDone():
        logger.info(f'retrieved URL from database: {x.title}/{x.url}')
        dlq.put(x.url)
      
      # Thread Main
      while 1:
        if Shutdown:
          return
        try:
          next = dlq.get(block = True, timeout=1)
        except Empty:
          logger.trace('downloader: queue empty')
          continue
        await self.download(next)

    async def download(self, next):
      logger.debug(f'self.urls: {self.urls}')
      logger.debug(f'next: {next}')
      logger.trace('Start Download Function')
      
      self.executor.submit(self.download_thread, *[next])
      
    def download_thread(self, url):
      """ url is the YT url for download """
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