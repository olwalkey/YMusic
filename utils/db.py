from sqlalchemy import create_engine, Column, String, Integer, Sequence, TIMESTAMP, Boolean, Enum, select, ForeignKey, update
from sqlalchemy.orm import sessionmaker, relationship, joinedload, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.exc import DuplicateColumnError, DBAPIError, OperationalError
from urllib.parse import urlparse, parse_qs


from bcrypt import gensalt
import argon2

from loguru import logger


from .config import config


Base = declarative_base()


class Tables():
    class Requests(Base):
        """Table for Storing Download Requests"""
        __tablename__ = 'requests'
        id = Column(Integer, autoincrement=True, primary_key=True)
        title = Column(String, default=None)
        url = Column(String, unique=True)
        queue_status = Column(
            Enum('queued', 'completed', name='queue_status'), default='queued')
        create_time = Column(TIMESTAMP, default=func.now())
        downloaded_time = Column(TIMESTAMP, default=None)
        downloaded_items = relationship(
            'Downloaded', back_populates='playlist')

    class Downloaded(Base):
        """Table for Storing Downloaded videos"""
        __tablename__ = 'downloaded'
        id = Column(Integer, autoincrement=True, primary_key=True)
        title = Column(String)
        playlist_url = Column(String, ForeignKey('requests.url'))
        path = Column(String)
        elapsed = Column(String)
        create_time = Column(TIMESTAMP, default=func.now())
        playlist = relationship('Requests', back_populates='downloaded_items')

    class Users(Base):
        """Table for Storing User Accounts and info"""
        __tablename__ = "users"
        id = Column(Integer, autoincrement=True, primary_key=True)
        Username = Column(String, unique=True)
        password = Column(String(50))
        salt = Column(String(29))
        admin = Column(Boolean(False))


def spliturl(url: list):
    """Splits url and returns the youtube video/playlist id

    Args:
        url (string): Youtube url Eg: https://www.youtube.com/watch?v=sVJEaYNOUNw

    Returns:
        string: End of youtube url
    """
    parsed_url = urlparse(url)  # type: ignore

    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get('v')
    playlist_id = query_params.get('list')
    if not playlist_id == None:
        url.append(playlist_id)
    else:
        url.append(video_id)
    return url


class interactions:
    def __init__(self):
        self.fetchNextDownload = (
            select(Tables.Requests)
            .where(Tables.Requests.queue_status == 'queued')
            .order_by(Tables.Requests.queue_status, Tables.Requests.create_time.desc())
        )

    def _connect(self):
        sessionmaker()
        self.engine = create_engine(
            f'postgresql+psycopg2://{config.db.user}@{
                config.db.host}:{config.db.port}/{config.db.db}',
            pool_size=5,
            max_overflow=0,
            echo=True,
            connect_args={"options": f"-c timezone={config.db.timezone}"}
        )
        self.conn = self.engine.connect()
        self.userConn = self.engine.connect()

    def check_conn(self) -> dict:
        try:
            conn = self.engine.connect()
            conn.close()
            return {"conn": True, "type": None, "error": None}
        except OperationalError as e:
            return {"conn": False, "type": "DBAPIError",  "error": e}
        except DBAPIError as e:
            return {"conn": False, "type": "DBAPIError", "error": e}

    def createEntry(self, url):
        """Creates An Entry in the Requests Table"""
        try:

            Tables.Requests(url=url)
            self.conn.commit()
            return {
                'data': {
                    'message': 'Download request received and queued',
                    'error': None
                }
            }
        except DuplicateColumnError as e:
            return {
                'data': {
                    'message': 'Duplicate Entry. Link already exists!',
                    'error': e
                }
            }

        except Exception as e:
            return {
                'data': {
                    'message': 'An unknown error occurred',
                    'error': e
                }
            }

    def create_tables(self):
        with self.engine.begin() as conn:
            Base.metadata.create_all(conn)
        conn.close()

    def fetchNextItem(self):
        """Returns next item to download"""
        fetch = self.conn.execute(statement=self.fetchNextDownload)

        return fetch

    def markVideoDownloaded(self, url, title):
        """Adds An entry in Downloaded Table with the downloaded item"""
        pass

    def markPlaylistDownloaded(self, url, title):
        """Marks A Playlist as completely Downloaded"""
        self.updateDownloaded = (
            update(Tables.Requests)
            .where(Tables.Requests.url == url)
            .values(
                title=title,
                queue_status="completed",
                downloaded_time=func.now()
            )
        )

    def new_user(self, user, user_pass):
        user_salt = gensalt()
        ph = argon2.PasswordHasher()
        hash = ph.hash(password=user_pass, salt=user_salt)
        Tables.Users(username=user, password=hash,
                     salt=user_salt)
