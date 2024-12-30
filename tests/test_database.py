import pytest
import time
from sqlalchemy.ext.asyncio import AsyncEngine
from loguru import logger

from utils.db import interactions, DBTypes
from utils import migrateDb


# NOTE: All tests that are purely reliant on sqlalchemy and not external lib's will be using postgresql
# As I don't think it's required to test it for postgres, mysql, maria, and sqlite. if it works in posstgres
# It will work in the others. It's not rocket science

@pytest.mark.asyncio
@pytest.mark.run()
async def test_connect():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    engine = await interaction.connect()

    assert isinstance(engine, AsyncEngine), f"Expected type 'AsyncEngine' but got {type(engine)}"

@pytest.mark.asyncio
@pytest.mark.run()
async def test_disconnect():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.setUsername("default")
    await interaction.setUsername("default")
    await interaction.connect()
    disc = await interaction.disconnect()
    assert disc == 1

@pytest.mark.asyncio
@pytest.mark.run()
async def test_reconnect():
    pass

@pytest.mark.asyncio
@pytest.mark.run()
async def test_testcon():

    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.setUsername("default")
    await interaction.setPassword("default")
    await interaction.connect()
    con: int = await interaction.testcon()

    assert con == 1


@pytest.mark.asyncio
@pytest.mark.run()
@pytest.mark.run(order=5)
async def test_postgres_migrations():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.postgresql, username="default", password="default")

    assert migrate == 1

@pytest.mark.asyncio
@pytest.mark.run()
@pytest.mark.run(order=6)
async def test_mysql_migrations():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.mysql)
    await interaction.setUsername("root")
    await interactions.setPassword("")
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.mysql, username='root', password='', port=3306)

    assert migrate == 1


@pytest.mark.asyncio
@pytest.mark.run()
@pytest.mark.run(order=7)
async def test_mariadb_migrations():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.mariadb)
    await interaction.setUsername("root")
    await interactions.setPassword("")
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.mariadb, username='root', password='', port=3307)

    assert migrate == 1


@pytest.mark.asyncio
@pytest.mark.run()
@pytest.mark.run(order=8)
async def test_sqlite_migrations():
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.sqlite)
    await interaction.connect()
    migrate: int = migrateDb(DBTypes.sqlite)

    assert migrate == 1


@pytest.mark.asyncio
@pytest.mark.run(order=99)
async def test_fetchNextItemEmpty():
    from utils.models import Requests
    interaction = interactions()

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.setUsername("default")
    await interaction.setPassword("default")
    await interaction.connect()

    item:Requests = await interaction.fetchNextItem()

    assert item == None

@pytest.mark.asyncio
@pytest.mark.run(order=100)
async def test_createPlaylistEntry():
    interaction = interactions()
    await interaction.setEnginetype(DBTypes.postgresql)
    
    await interaction.setUsername("default")
    await interaction.setPassword("default")

    await interaction.connect()
    
    myassr = await interaction.createEntry("OLAK5uy_nwrFWHHh1oNbygnCMaRFwhw5o8BtIYxLk")
    assert myassr == {
                    'data': {
                    'message': f'New request with ID: 1 has been created',
                    'error': "None"
                }
            }

@pytest.mark.asyncio
@pytest.mark.run(order=100)
async def test_createVideoEntry():
    interaction = interactions()
    await interaction.setUsername("default")
    await interaction.setPassword("default")

    await interaction.setEnginetype(DBTypes.postgresql)
    await interaction.connect()

@pytest.mark.asyncio
@pytest.mark.run(order=101)
async def test_duplicateEntry():
    interaction = interactions()
    await interaction.setEnginetype(DBTypes.postgresql)

    await interaction.setUsername("default")
    await interaction.setPassword("default")

    await interaction.connect()

    myassr = await interaction.createEntry("OLAK5uy_nwrFWHHh1oNbygnCMaRFwhw5o8BtIYxLk")
    logger.error(myassr)
    assert myassr == {
                'data':{
                    'message': f'Duplicate Entry. Link already exists',
                    'error': '3000',
                }}


@pytest.mark.asyncio
@pytest.mark.run(order=102)
async def test_fetchNextItemPopulated():
    pass



