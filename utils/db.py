from sqlalchemy import except_, insert, select, update
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func as sqlfunc
from sqlalchemy.exc import DuplicateColumnError, DBAPIError, IntegrityError, OperationalError
from urllib.parse import urlparse, parse_qs
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker

from typing import Any, TypedDict

from bcrypt import gensalt
import argon2

from loguru import logger


from .config import config

from . import models as Tables



class DBInfo(TypedDict):
    database: str
    driver: str
    port: int


class DBTypes():
    postgresql: DBInfo = {"database": "postgresql", "driver": "asyncpg", "port": 5432}
    mysql: DBInfo = {"database": "mysql", "driver": "aiomysql", "port": 3306}
    mariadb: DBInfo = {"database": "mysql", "driver": "aiomysql", "port": 3306}
    sqlite: DBInfo = {"database": "sqlite", "driver": "aiosqlite", "port": 0}



class interactions:
    engine: AsyncEngine
    engineType: DBInfo = DBTypes.postgresql

    username: str = "default"
    password: str = "default"
    host: str = "localhost"
    port: int = 0
    database: str = "youtube"

    @classmethod
    async def setEnginetype(cls, etype: DBInfo):
        cls.engineType = etype

    @classmethod
    async def setUsername(cls, username) -> None:
        cls.username = username

    @classmethod
    async def setPassword(cls, password) -> None:
        cls.password = password
    
    @classmethod
    async def setHost(cls, host) -> None:
        cls.host = host
    
    @classmethod
    async def setPort(cls, port) -> None:
        cls.port = port
    
    @classmethod
    async def setDatabase(cls, database) -> None:
        cls.database = database

    @classmethod
    async def connect(cls) -> AsyncEngine:
        """
            Connects to the database and persist a connection using a connection pool
            ---
        """
        if cls.port == 0:
            cls.port = cls.engineType["port"]
        try:
            if not cls.engineType['database'] == "sqlite":
                cls.engine = create_async_engine(
                    url=f"{cls.engineType['database']}+{cls.engineType['driver']}://{cls.username}:{cls.password}@{cls.host}:{cls.port}/{cls.database}",
                    pool_size=10,
                    max_overflow=10,
                    pool_timeout=30,
                    echo=True if config.debug is True else False,
                    pool_pre_ping=True,
                )

            else:
                cls.engine = create_async_engine(
                    url=f"{cls.engineType['database']}+{cls.engineType['driver']}:///{cls.database}.sqlite",
                    echo=True if config.debug is True else False,
                    pool_pre_ping=True,
                )


            cls.AsyncSession = async_sessionmaker(cls.engine, class_=AsyncSession, expire_on_commit=False)


        except Exception as e:
            logger.error("Failed to connect to the database!")
            logger.error(e)
        if not isinstance(cls.engine, AsyncEngine):
            logger.error(f"engine Responded with type: {type(cls.engine)}")
            exit()

        return cls.engine

    @classmethod
    async def disconnect(cls) -> int:
        try:
            await cls.engine.dispose()
            return 1
        except Exception as e:
            logger.error(e)
            return 0


    @classmethod
    async def reconnect(cls) -> int:
        """
            Attempts to reconnect to the database if testcon fails
            ---
        """
        try:
            await cls.disconnect()
            await cls.connect()
            return 1
        except Exception as e:
            logger.error(e)
            return 0

    @classmethod
    async def testcon(cls) -> int:
        """
            Tests connection to the datbabase
            ---
            Returns 0 if failed
            Returns 1 if Success
        """

        try:
            async with cls.engine.connect() as connection:
                logger.error(connection)
                return 1
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return 0

    @classmethod
    async def createEntry(
        cls,
        uri: str
    ) -> dict[str, dict[str, str]]:
        """
            Creates a new entry in the requests table to download once it's called in queue
            ---
        """
        try:
            async with cls.AsyncSession() as session:
                new_entry = Tables.Requests(url=uri)
                session.add(new_entry)
                await session.commit()
                logger.trace(f"New Request with ID: {new_entry.id}")

                return {
                        'data': {
                        'message': f'New request with ID: {new_entry.id} has been created',
                        'error': "None"
                    }
                }
        except DuplicateColumnError as e:
            return {
                'data':{
                    'message': f'Duplicate Entry. Link already exists',
                    'error': '3000'
                }
            }
        except IntegrityError as e:
            return {
                'data':{
                    'message': f'Duplicate Entry. Link already exists',
                    'error': '3000'
                }
            }




    @classmethod
    async def fetchNextItem(cls) -> Tables.Requests | None:
        """
            Fetches next eligible item for download from the database
            ---
        """
        query = (
            select(Tables.Requests)
            .where(Tables.Requests.queue_status == 'queued')
            .order_by(Tables.Requests.id.asc())
            .limit(1)
        )
        try:
            async with cls.AsyncSession() as session:
                result = await session.execute(query)
                item: Tables.Requests = result.scalar_one_or_none()
                logger.debug(f"""
                             result: {result.__dict__}
                             item: {item}
                """)
                if isinstance(item, Tables.Requests):
                    logger.trace(item)
                    return item
                else:
                    raise KeyError

        except Exception as e:
            logger.error(f"Failed to fetch next item {e}")
            return None


    @classmethod
    async def newDownloaded(
        cls,
        playlisturl: Any,
        url: Any,
        title: Any,
        download_path: Any,
        elapsed: Any
    ) -> None:
        """
            Creates a new entry in the Downloaded Table
            and marks it downloaded with all relevent info
            ---
        """
        try:
            async with cls.AsyncSession() as session:
                newItem = Tables.Downloaded(playlist_url=playlisturl, url=url, title=title, path=download_path, elapsed=str(elapsed))
                session.add(newItem)
                await session.commit()
                logger.trace(f"New Download with ID: {newItem.id}")

        except Exception as e:
            logger.error(e)

    @classmethod
    async def playlistDownloaded(
            cls,
            url: str,
            name: str,
            extractor: str
    ) -> None:
        """
            Takes a playlist id and set's it's status to completed in the db  

            ---
        """
        try:
            query = (
                update(Tables.Requests)
                .where(Tables.Requests.url==url)
                .values(title=name, extractor=extractor, download_time=sqlfunc.now(), queue_status="completed")

            )
            async with cls.AsyncSession() as session:
                await session.execute(query)

                await session.commit()

        except Exception as e:
            logger.error(e)


    @classmethod
    async def newUser(
            cls,
            username: str,
            hash: str,
            salt: str
    ) -> None:
        """
            Creates a new entry in the database for a new user
            ---
        """
        pass

    @classmethod
    async def fetchUser(cls, username: str) -> None:
        """
        Fetches a user from the database
        ---
        """
        pass


    @classmethod
    async def verifyUser(cls, username, password) -> None:
        """
            Verify A username and hash against it in the database
            ---
        """
        pass


