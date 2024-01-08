from sqlalchemy import create_engine, Column, String, Integer, Sequence, TIMESTAMP, Boolean, Enum, select, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import urlparse, parse_qs
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.future import select
from sqlalchemy.sql import func
from munch import munchify
import yaml
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

Base = declarative_base()

with open("./config.yaml") as f:
    yamlfile = yaml.safe_load(f)
config = munchify(yamlfile)



class Playlist(Base):
  __tablename__ = 'playlists'
  id = Column(Integer, autoincrement=True, primary_key=True)
  title = Column(String, default=None)
  url = Column(String, unique=True)
  queue_status = Column(Enum('queued', 'in_progress', 'completed', name='queue_status'), default='queued')
  create_time = Column(TIMESTAMP, default=func.now())
  downloaded_time = Column(TIMESTAMP, default=None)
  downloaded_items = relationship('Downloaded', back_populates='playlist')

class Downloaded(Base):
  __tablename__ = 'downloaded'
  id = Column(Integer, autoincrement=True, primary_key=True)
  title = Column(String)
  playlist_url = Column(String, ForeignKey('playlists.url')) # New line
  url = Column(String)
  path = Column(String)
  elapsed = Column(String)
  create_time = Column(TIMESTAMP, default=func.now())
  playlist = relationship('Playlist', back_populates='downloaded_items')





def spliturl(url):
  """Splits urls the exact same way as the main.py script for consistant url grabbing

  Args:
      url (string): Youtube url Eg: https://www.youtube.com/watch?v=sVJEaYNOUNw&t=162s

  Returns:
      string: End of youtube url
  """
  parsed_url = urlparse(url)

  query_params = parse_qs(parsed_url.query)
  video_id = query_params.get('v')
  playlist_id = query_params.get('list')
  if not playlist_id == None:
      url.append(playlist_id)
  else:
      url.append(video_id)
  return url



class Database:
    engine = None
    async_session = None

    def __init__(self):
        self.connect(config.db.host, config.db.port, config.db.user, config.db.password, config.db.db)

    def connect(self, host:config.db.host, port:config.db.port, user:config.db.user, password:config.db.password, database:config.db.db):
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}",
            echo=False  # Set to False in production
        )

        self.async_session = sessionmaker(
          bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def QueueNotDone(self):
        async with self.async_session() as session:
          queued_items = await session.execute(
            select(Playlist).filter(Playlist.queue_status == 'queued').order_by(Playlist.create_time.asc())
          )
          return queued_items.scalars().all()
    
    async def mark_playlist_downloaded(self, url, title):
      async with self.async_session() as session:
        query = session.query(Playlist)
        query = query.filter(Playlist.url == url)
        await session.execute(
          query.update({Playlist.queue_status: 'completed'}),
          query.update({Playlist.title: title}),
          query.update({Playlist.downloaded_time: func.now()})
        )
        await session.commit()

    async def mark_video_downloaded(self, url, title, download_path, elapsed):
      async with self.async_session() as session:
        async with session.begin():
          new_download = Downloaded(title=title, url=url, path=download_path,elapsed=elapsed )
          session.add(new_download)
    
    async def new_queue(self, url):
      async with self.async_session() as session:
        async with session.begin():
          new_queue = Playlist(title=None, url=url, queue_status='queued')
          session.add(new_queue)

    async def db_create(self):
      async with self.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
                
                
                
    async def reconnect(self):
      await self.async_session.close()
      self.connect()

    async def __aenter__(self):
      return self

    async def __aexit__(self, exc_type, exc_value, traceback):
      await self.async_session.close()
      if exc_type is not None:
        raise
