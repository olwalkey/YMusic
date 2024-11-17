from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.exc import DuplicateColumnError, DBAPIError, OperationalError
from urllib.parse import urlparse, parse_qs


from bcrypt import gensalt
import argon2

from loguru import logger


from .config import config

from . import models as Tables
from .models import Base


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
        self.engine = create_engine(
            f'postgresql+psycopg2://{config.db.user}:{config.db.password}@{
                config.db.host}:{config.db.port}/{config.db.db}',
            pool_size=5,
            max_overflow=0,
            echo=False,
            connect_args={"options": f"-c timezone={config.db.timezone}"}
        )
        self.conn = self.engine.connect()
        self.userConn = self.engine.connect()
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def check_conn(self) -> dict:
        try:
            conn = self.engine.connect()
            conn.close()
            return {"conn": True, "type": None, "error": None}
        except OperationalError as e:
            return {"conn": False, "type": "DBAPIError",  "error": e}
        except DBAPIError as e:
            return {"conn": False, "type": "DBAPIError", "error": e}

    def createEntry(self, id):
        """Creates An Entry in the Requests Table"""
        try:
            with self.session() as session:
                new_request = Tables.Requests(url=id)
                session.add(new_request)
                session.commit()

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


    def fetchNextItem(self):
        """Returns next item to download"""
        fetch = self.conn.execute(statement=self.fetchNextDownload)
        if fetch is None:
            return None
        return fetch.fetchone()

    def markVideoDownloaded(
        self,
        playlisturl,
        url,
        title,
        download_path,
        elapsed
    ):
        """Adds An entry in Downloaded Table with the downloaded item"""
        try:
            with self.session() as session:
                logger.debug(session)
                related_playlist = session.query(
                    Tables.Requests).filter_by(url=playlisturl).first()
                if not related_playlist:
                    logger.error(f"No playlist found for url {url}")
                new_download = Tables.Downloaded(
                    title=title,
                    url=url,
                    path=download_path,
                    elapsed=elapsed,
                    playlist=related_playlist)
                logger.debug(new_download)
                session.add(new_download)
                session.commit()
        except Exception as e:
            logger.error(e)

    def markPlaylistDownloaded(self, url, title, extractor):
        """Marks A Playlist as completely Downloaded"""
        with self.session() as session:
            logger.debug("")
            self.updateDownloaded = (
                update(Tables.Requests)
                .where(Tables.Requests.url == url)
                .values(
                    title=title,
                    queue_status="completed",
                    downloaded_time=func.now(),
                    extractor=extractor,
                )
            )
            logger.debug(self.updateDownloaded)
            session.execute(self.updateDownloaded)
            session.commit()

    def fetchUser(self, user):
        """Checks if A user exists by username"""
        fetchedUser = (
            select(Tables.Users)
            .where(Tables.Users.username == user))
        try:
            fetch = self.conn.execute(statement=fetchedUser)
            return fetch.fetchone()

        except Exception as e:
            logger.error(e)
            return None

    def new_user(self, user: str, user_pass: str):
        """Created A new user using username and password"""
        myfetch = self.fetchUser(user)
        if myfetch == None:
            myfetch = []

        if len(myfetch) != 0:  # type: ignore
            logger.error('User already exists')
            return "User already Exists"
        else:
            user = user.lower()
            user_salt = gensalt()
            ph = argon2.PasswordHasher()
            hash = ph.hash(password=user_pass, salt=user_salt)
            with self.session() as session:
                new_user = Tables.Users(username=user, password=hash,
                                        salt=user_salt, admin=False)
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                return new_user

    def verify_user(self, user: str, password: str):
        """Verify the sent password to the stored password"""
        user_hash = self.fetchUser(user)
        if user_hash is None:
            return False
        hashed_password = user_hash[2]
        ph = argon2.PasswordHasher()
        ph.verify(hashed_password, password)
        ph.check_needs_rehash(hashed_password)
        return True, user_hash[1]
