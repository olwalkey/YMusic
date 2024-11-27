import pytest
import time
import pytest_docker
from sqlalchemy.ext.asyncio import AsyncEngine
from loguru import logger

from utils.db import interactions, DBTypes
from utils import migrateDb


#@pytest.fixture(scope='session')
#def docker_postgres(docker_services):
#    docker_services.start('postgresql')
#    public_port = docker_services.wait_for_service("postgresql", 5432)
#    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
#    return url
#
#@pytest.fixture(scope='session')
#def docker_mysql(docker_services):
#    docker_services.start('mysql')
#    public_port = docker_services.wait_for_service("mysql", 3306)
#    dsn = "{docker_services.docker_ip}:{public_port}".format(**locals())
#    return dsn
#
#
#@pytest.fixture(scope='session')
#def docker_maria(docker_services):
#    docker_services.start('mysql')
#    public_port = docker_services.wait_for_service("mariadb", 3306)
#    shit = {"ip": docker_services.docker_ip, "port": docker_services}
#    logger.error(shit)
#    return shit


@pytest.mark.asyncio
@pytest.mark.run()
async def test_connect():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    engine = await interaction.connect()

    assert isinstance(engine, AsyncEngine), f"Expected type 'AsyncEngine' but got {type(engine)}"

@pytest.mark.asyncio
@pytest.mark.run()
async def test_testcon():
    
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.setUsername("default")
    await interaction.setUsername("default")
    await interaction.connect()
    con: int = await interaction.testcon()

    assert con == 1


@pytest.mark.asyncio
@pytest.mark.run()
async def test_postgres_migrations():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.postgresql, username="default", password="default")

    assert migrate == 1

# FIXME: ALl of these tests just don't work because pymysql isn't compatible 

#@pytest.mark.asyncio
#@pytest.mark.run()
#async def test_mysql_migrations():
#    interaction = interactions()
#
#    await interaction.setEnginetype(DBTypes.mysql)
#    await interaction.setUsername("root")
#    await interaction.connect()
#    migrate: int = migrateDb(DBTypes.mysql)
#
#    assert migrate == 1
#
#
#@pytest.mark.asyncio
#@pytest.mark.run()
#async def test_mariadb_migrations():
#    interaction = interactions()
#
#    await interaction.setEnginetype(DBTypes.mariadb)
#    await interaction.setUsername("root")
#    await interaction.connect()
#    migrate: int = migrateDb(DBTypes.mariadb)
#
#    assert migrate == 1


@pytest.mark.asyncio
@pytest.mark.run()
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

