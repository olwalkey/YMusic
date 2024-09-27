from .downloader import Downloader

from .db import interactions

interaction = interactions()
interaction._connect()
youtube = Downloader()
