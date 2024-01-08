import yt_dlp
from munch import munchify
from typing import Optional


if __name__ == 'downloader':
  from db import Database
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
  db = Database()

  async def fill(self):
    self.myqueue = await self.db.QueueNotDone()
    return self.myqueue

class Downloader:
  StatusStarted=False
  Started=False
  web_use=False
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
  urls=[]
  db = Database()

  def __init__(
    self, host:Optional[str]=None, 
    download_path:Optional[str]='downloads/', 
    port:Optional[int]=5000,
  ):
    if not host == None:
      self.web_use = True
      self.host = host
      self.port = port
      self.download_path = download_path



  def progress_hook(self, d):
    d = munchify(d)
    
    if d.status == 'error':
      pass
    
    if d.status == 'finished':
      print(f'Done Downloading "{d["filename"]}"')
      self.StatusStarted = False
      self.filename = d['filename']
      self.time_elapse = d['elapsed']
    
    if d.status == 'downloading':
      if not self.StatusStarted:
        print(f'Now Downloading "{d["tmpfilename"]}"')    
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
      self.Status = 'Finished'
      pass

  def ydl_opts(self):
    ydl_opts = {
      'ratelimit': 500000, # Kilobytes
      'logger': MyLogger(),
      'breakonexisting': True,
      'progress_hooks': [self.progress_hook],
      'postprocessor_hooks': [self.postprocessor_hooks],
      'writethumbnail': True,
      'outtmpl': 'downloads/%(playlist_title)s/%(title)s.%(ext)s',
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
  
  async def queue_dl(self, urls):
    if not self.Started:
      self.download(urls)
    else:
      for url in urls:
        self.urls.append(urls[url])


  def download(self, urls):
    for url in self.urls:
      with yt_dlp.YoutubeDL(self.ydl_opts()) as ydl:
        ydl.download(urls[url])
        self.db.mark_video_downloaded(self.title, self.url, self.download_path, self.time_elapse)
      self.db.mark_playlist_downloaded(urls[url], self.title)
      continue
    self.Started = False

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
  
