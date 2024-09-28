from .db import interactions, Tables

interaction = interactions()
interaction._connect()

from .downloader import Downloader

youtube = Downloader()
