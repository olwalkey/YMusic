from sqlalchemy import except_, select, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.exc import DuplicateColumnError, DBAPIError, OperationalError
from urllib.parse import urlparse, parse_qs
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from typing import TypedDict

from bcrypt import gensalt
import argon2

from loguru import logger


from .config import config

from . import models as Tables
from .models import Base


class DBInfo(TypedDict):
    database: str
    driver: str


class DBTypes():
    postgresql: DBInfo = {"database": "postgresql", "driver": "asyncpg"}
    mysql: DBInfo = {"database": "mysql", "driver": "aiomysql"}
    mariadb: DBInfo = {"database": "mysql", "driver": "aiomysql"}
    sqlite: DBInfo = {"database": "sqlite", "driver": "aiosqlite"}



class interactions:
    dbtest:int = 0
    engine: AsyncEngine
    engineType: DBInfo = DBTypes.postgresql

    username: str = "postgres"
    password: str = "supersecurepass"
    host: str = "localhost"
    port: int = 5432
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
        try:
            if not cls.engineType['database'] == "sqlite":
                cls.engine = create_async_engine(
                    url=f"{cls.engineType['database']}+{cls.engineType['driver']}://{cls.username}:{cls.password}@{cls.host}:{cls.port}/{cls.database}",
                    pool_size=10,
                    max_overflow=10,
                    pool_timeout=30,
                    echo=True,
                )
            else:
                cls.engine = create_async_engine(
                    url=f"{cls.engineType['database']}+{cls.engineType['driver']}:///{cls.database}.sqlite",
                    pool_size=10,
                    max_overflow=10,
                    pool_timeout=30,
                    echo=True,
                )


        except Exception as e:
            logger.error("Failed to connect to the database!")
            logger.error(e)
        if not isinstance(cls.engine, AsyncEngine):
            logger.error(f"engine Responded with type: {type(cls.engine)}")
            exit()

        return cls.engine


    @classmethod
    async def reconnect(cls) -> None:
        """
            Attempts to reconnect to the database if testcon fails
            ---
        """
        pass

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
                return 1
        except Exception as e:
            print("Connection failed:", str(e))
            return 0

    @classmethod
    async def createEntry(cls) -> None:
        """
            Creates a new entry in the requests table to download once it's called in queue
            ---
        """
        pass


    @classmethod
    async def fetchNextItem(cls) -> None:
        """
            Fetches next eligible item for download from the datbase
            ---
        """
        pass

    @classmethod
    async def newDownloaded(cls) -> None:
        """
            Creates a new entry in the Downloaded Table
            and marks it downloaded with all relevent info
            ---
        """
        pass

    @classmethod
    async def playlistDownloaded(cls) -> None:
        """
            Takes a playlist id and set's it's status to completed in the db  

            ---
        """
        pass

    @classmethod
    async def newUser(cls) -> None:
        """
            Creates a new entry in the database for a new user
            ---
        """
        pass

    @classmethod
    async def fetchUser(cls) -> None:
        """
        Fetches a user from the database
        ---
        """
        pass


    @classmethod
    async def verifyUser(cls) -> None:
        """
            Verify A username and hash against it in the database
            ---
        """
        pass


