# db.py manages database
# app.py requires
from sqlalchemy import create_engine, Column, String, Integer, Sequence, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.sql import func
from munch import munchify
import yaml

Base = declarative_base()

with open("./config.yaml") as f:
  yamlfile=yaml.safe_load(f)
config = munchify(yamlfile)


class Downloaded(Base):
  __tablename__ = 'downloaded'
  id = Column(Integer, autoincrement=True, primary_key=True)
  title = Column(String)
  url = Column(String)
  path = Column(String)
  elapsed = Column(String)
  create_time = Column(TIMESTAMP, default=func.now())


class Albums(Base):
  __tablename__ = 'albums'
  id = Column(Integer, autoincrement=True, primary_key=True)
  title = Column(String)
  url = Column(String)
  create_time = Column(TIMESTAMP, default=func.now())


class Queue(Base):
  __tablename__ = 'queue'
  id = Column(Integer, autoincrement=True, primary_key=True)
  url = Column(String)
  downloaded = Column(String)
  create_time = Column(TIMESTAMP, default=func.now())


class Database:
  engine = None
  session = None

  def __init__(self, host:str=config.db.host, port:int=config.db.port, user:str=config.db.user, password:str=config.db.password, database:str=config.db.db):
    self.connect(host, port, user, password, database)
    
  def connect(self, host, port, user, password, database):
    try:
      self.engine = create_engine(
        url=f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        )
      self.session = Session(bind=self.engine)
    except Exception as e:
      print(f"Error connecting to the database: {e}")
      exit()
  
  def __del__(self):
    if hasattr(self, 'session') and self.session:
      self.session.close()
      del self.session
    
  def db_create(self):
    try:
      Base.metadata.create_all(self.engine)
    except Exception as e:
      print(f'An Error Occured: {e}')
      exit()

  def reconnect(self):
    self.__del__()
    self.connect()


class SQL:  
  db = Database
  
  def write_to_videoDB(self, title, url, download_path, elapsed):
    self.db.db_create()
    
    new_downloaded = Downloaded(title=title, url=url, download_path=download_path, elapsed=elapsed)
    
    self.db.session.add(new_downloaded)
    self.db.session.commit()
  
  def write_to_albumDB(self, title, url):
    self.db.db_create()
    
    new_album = Albums(title=title, url=url)
    
    self.db.session.add(new_album)
    self.db.session.commit()

  def new_queue(self, downloaded, url):
    self.db.db_create()
    
    new_album = Queue(url=url, downloaded=downloaded)
    
    self.db.session.add(new_album)
    self.db.session.commit()
