import yt_dlp
from munch import munchify
from typing import Optional
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from pytube import Playlist
import asyncio
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

debug_init(False, False)

if __name__ != '__main__':
  try:
    from db import Database
  except ImportError:
    try: 
      from .db import Database
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
  if __name__ != "__main__":
    db = Database()
  else:
    pass
  def fill(self):
    """returns all non downloaded items in the database

    Returns:
        dict: id: url
    """
    self.myqueue = self.db.QueueNotDone()
    return self.myqueue



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

  urls=[]
  if __name__ != "__main__":
    db = Database()
  else: 
    pass
  
  loop = asyncio.get_event_loop()
  executor = ThreadPoolExecutor(max_workers=1)
  loop.set_default_executor(executor)


  def __init__(
    self, host:Optional[str]=None, 
    download_path:Optional[str]='downloads/', 
    port:Optional[int]=5000,
  ):
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
        logger.trace(f'Now Downloading "{d["tmpfilename"]}"')    
        self.StatusStarted = True

      self.filename = d['tmpfilename']
      self.percent = d['_percent_str']
      self.eta = d['_eta_str']
        
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
      # 'ratelimit': 500000, # Kilobytes
      'logger': MyLogger(),
      'breakonexisting': True,
      'progress_hooks': [self.progress_hook],
      'postprocessor_hooks': [self.postprocessor_hooks],
      'writethumbnail': True,
      'outtmpl': 'downloads/%(playlist_title)s/%(autonumber)s - %(title)s.%(ext)s',
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

  def playlist_title(self):
    ydl_opts = {
      'quiet': True,
      'extract_flat': True
    }
    return ydl_opts
  
  async def queue_dl(self, qurls: Optional[list] = None):
    logger.trace(f'Started: {self.Started}')
    logger.debug(qurls)
    
    if qurls == None:
      q = queue()
      q.fill()
    elif not self.Started:
      logger.trace('Starting Download')
      self.urls = qurls
      await self.download()
    else:
      logger.trace('Print_appending stuff')
      for url in qurls:
        self.urls.append(url)

  async def download(self):
    logger.debug(f'self.urls: {self.urls}')
    logger.trace('Start Download Function')
    
    self.executor.submit(self.download_thread)
    
  def download_thread(self):
    logger.trace('Start for loop')
    for url in self.urls:
      with yt_dlp.YoutubeDL(self.playlist_title()) as ydl:
        result = ydl.extract_info(url, download=False)
        title_url = result['url']
        playlist = Playlist(title_url)
        self.PlaylistTitle = playlist.title

      with yt_dlp.YoutubeDL(self.ydl_opts()) as ydl:
        self.playlist_url=url
        logger.trace('Start with statement')
        ydl.download(url)

        logger.debug('At the end')
        self.db.mark_playlist_downloaded(url, self.PlaylistTitle)
        logger.debug("It's over")


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
  
