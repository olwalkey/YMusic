from .db import interactions

interaction = interactions()
interaction._connect()

from .downloader import Downloader # type: ignore


youtube = Downloader()
