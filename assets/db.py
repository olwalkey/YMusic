from sqlalchemy import create_engine, Column, String, Integer, Sequence, TIMESTAMP, Boolean, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from munch import munchify
import yaml
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

Base = declarative_base()

with open("./config.yaml") as f:
    yamlfile = yaml.safe_load(f)
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
    url = Column(String, unique=True)
    downloaded = Column(Boolean, default=False)
    create_time = Column(TIMESTAMP, default=func.now())

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
                select(Queue).filter(Queue.downloaded.is_(False)).order_by(Queue.create_time.desc())
            )
            return queued_items.scalars().all()

    async def new_queue(self, downloaded, url):
        async with self.async_session() as session:
            async with session.begin():
                new_queue = Queue(url=url, downloaded=downloaded)
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

# Your other methods in Database class can also be converted to async methods.
