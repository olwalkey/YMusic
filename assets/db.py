# db.py manages database
# app.py requires
from sqlalchemy import create_engine, Column, String, Integer, Sequence, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.sql import func

Base = declarative_base()

class downloaded(Base):
  __tablename__ = 'downloaded'
  id = Column(Integer, autoincrement=True, primary_key=True)
  title = Column(String)
  url = Column(String)
  path = Column(String)
  elapsed = Column(String)
  create_time = Column(TIMESTAMP, default=func.now())

class albums(Base):
  __tablename__ = 'albums'
  id = Column(Integer, autoincrement=True, primary_key=True)
  title = Column(String)
  url = Column(String)
  create_time = Column(TIMESTAMP, default=func.now())

class albums(Base):
  __tablename__ = 'albums'
  id = Column(Integer, autoincrement=True, primary_key=True)
  url = Column(String)
  downloaded = Column(String)
  create_time = Column(TIMESTAMP, default=func.now())


from munch import munchify
import yaml
try:
  with open("./config.yaml") as f:
      yamlfile=yaml.safe_load(f)
except yaml.YAMLError:
  with open('../config.yaml') as f:
    yamlfile=yaml.safe_load(f)

config = munchify(yamlfile)

class database:
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
      if self.conn is not None:
          self.conn.close()

  def db_create(self):
    try:
      Base.metadata.create_all(self.engine)
    except Exception as e:
      print(f'An Error Occured: {e}')
      exit()

  def reconnect(self):
    self.__del__()
    self.connect()


class sql:  
  db = database
  def write_to_videoDB(self, title, url, download_path, elapsed):
    self.db.db_create()
    
    new_downloaded = downloaded(title, url, download_path, elapsed)
    
    self.db.session.add(new_downloaded)
    self.db.session.commit()
  
  def write_to_albumDB(self, title, url):
    self.db.db_create()
    
    new_album = albums(title, url)
    
    self.db.session.add(new_album)
    self.db.session.commit()

  def new_queue(self, downloaded, url):
    self.db.db_create()
    
    new_album = (url, downloaded)
    
    self.db.session.add(new_album)
    self.db.session.commit()
