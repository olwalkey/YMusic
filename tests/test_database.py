import pytest
import pytest_docker
import time
from sqlalchemy.ext.asyncio import AsyncEngine
from loguru import logger

from utils.db import interactions, DBTypes
from utils import migrateDb


@pytest.fixture(scope="session")
def start_services(docker_services):
    docker_services.start_all()


@pytest.mark.asyncio
@pytest.mark.run(order=1)
async def test_connect(docker_services):
    logger.error(type(docker_services))
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    engine = await interaction.connect()

    assert isinstance(engine, AsyncEngine), f"Expected type 'AsyncEngine' but got {type(engine)}"

@pytest.mark.asyncio
@pytest.mark.run(order=2)
async def test_testcon(docker_services):
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.connect()
    con: int = await interaction.testcon()

    assert con == 1


@pytest.mark.asyncio
@pytest.mark.run(order=3)
async def test_postgres_migrations(docker_services):
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.postgresql)

    assert migrate == 1

@pytest.mark.asyncio
@pytest.mark.run(order=4)
async def test_mysql_migrations(docker_services):
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.mysql)
    await interaction.setUsername("root")
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.mysql)

    assert migrate == 1


@pytest.mark.asyncio
@pytest.mark.run(order=5)
async def test_mariadb_migrations():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.mariadb)
    await interaction.setUsername("root")
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.mariadb)

    assert migrate == 1


@pytest.mark.asyncio
@pytest.mark.run(order=6)
async def test_sqlite_migrations():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.sqlite)
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.sqlite)

    assert migrate == 1


@pytest.mark.asyncio
async def test_sqlite():
    pass

@pytest.mark.asyncio
async def test_mysql():
    pass

@pytest.mark.asyncio
async def test_mariadb():
    pass

@pytest.mark.asyncio
async def test_postgres():
    pass

@pytest.mark.asyncio
async def test_createEntry():
    pass

@pytest.mark.asyncio
async def test_duplicateEntry():
    pass

@pytest.mark.asyncio
async def test_fetchNextItem():
    pass

@pytest.mark.asyncio
@pytest.mark.run(order=100)
async def test_reconnect():
    pass

@pytest.mark.asyncio
@pytest.mark.run(order=101)
async def test_disconnect():
    pass

