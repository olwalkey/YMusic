import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from loguru import logger

from utils.db import interactions, DBTypes
from utils import migrateDb


User = "default"
Password = "default"
Host = "127.0.0.1"
EngineType = DBTypes.postgresql

expect_duplicateEntry = {
    'data': {
        'message': f'Duplicate Entry. Link already exists',
        'error': '3000',
    }}


@pytest.mark.asyncio
@pytest.mark.run(order=0)
@pytest.mark.timeout(10)
async def test_connect():
    interaction = interactions()

    await interaction.setEnginetype(EngineType)
    await interaction.setUsername(User)
    await interaction.setUsername(Password)

    engine = await interaction.connect()

    assert isinstance(engine, AsyncEngine), f"Expected type 'AsyncEngine' but got {
        type(engine)}"


@pytest.mark.asyncio
@pytest.mark.run(order=1)
@pytest.mark.timeout(10)
async def test_disconnect():
    interaction = interactions()

    await interaction.setEnginetype(EngineType)
    await interaction.setUsername(User)
    await interaction.setUsername(Password)
    await interaction.connect()
    disc = await interaction.disconnect()
    assert disc == 1


@pytest.mark.asyncio
@pytest.mark.run(order=2)
@pytest.mark.timeout(10)
async def test_reconnect():
    interaction = interactions()

    await interaction.setEnginetype(EngineType)
    await interaction.setUsername(User)
    await interaction.setPassword(Password)
    await interactions.connect()
    recon = await interactions.reconnect()

    assert recon == 1


@pytest.mark.asyncio
@pytest.mark.run(order=2)
@pytest.mark.timeout(10)
async def test_testcon():

    interaction = interactions()

    await interaction.setEnginetype(EngineType)
    await interaction.setUsername(User)
    await interaction.setPassword(Password)
    await interaction.setPort(5432)
    await interaction.connect()
    con: int = await interaction.testcon()

    assert con == 1


@pytest.mark.asyncio
@pytest.mark.run(order=3)
@pytest.mark.timeout(10)
async def test_migrations():
    interaction = interactions()

    await interaction.setEnginetype(EngineType)
    await interaction.connect()
    migrate: int = migrateDb("postgres", username=User, password=Password)

    assert migrate == 1


@pytest.mark.asyncio
@pytest.mark.run(order=4)
@pytest.mark.timeout(10)
async def test_fetchNextItemEmpty():
    from utils.models import Requests
    interaction = interactions()

    await interaction.setEnginetype(EngineType)
    await interaction.setUsername(User)
    await interaction.setPassword(Password)
    await interaction.connect()

    item: Requests = await interaction.fetchNextItem()

    assert item == None


@pytest.mark.asyncio
@pytest.mark.run(order=5)
async def test_createPlaylistEntry():
    interaction = interactions()
    await interaction.setEnginetype(EngineType)
    await interaction.setHost(Host)
    await interaction.setUsername(User)
    await interaction.setPassword(Password)

    await interaction.connect()

    myassr = await interaction.createEntry("OLAK5uy_nwrFWHHh1oNbygnCMaRFwhw5o8BtIYxLk")
    assert myassr == {
        'data': {
            'message': f'New request with ID: 1 has been created',
            'error': "None"
        }
    }


@pytest.mark.asyncio
@pytest.mark.run(order=6)
async def test_createVideoEntry():
    interaction = interactions()

    await interaction.setUsername(User)
    await interaction.setPassword(Password)

    await interaction.setEnginetype(EngineType)
    await interaction.connect()


@pytest.mark.asyncio
@pytest.mark.run(order=30)
async def test_duplicateEntry():
    interaction = interactions()
    await interaction.setEnginetype(EngineType)

    await interaction.setUsername(User)
    await interaction.setPassword(Password)
    await interaction.setPort(5432)

    await interaction.connect()

    myassr = await interaction.createEntry("OLAK5uy_nwrFWHHh1oNbygnCMaRFwhw5o8BtIYxLk")
    print(myassr)
    assert myassr == expect_duplicateEntry


@pytest.mark.asyncio
@pytest.mark.run(order=30)
async def test_fetchNextItemPopulated():
    from utils.models import Requests

    interaction = interactions()
    await interaction.setEnginetype(EngineType)

    await interaction.setUsername(User)
    await interaction.setPassword("default")

    await interaction.connect()

    item: Requests = await interaction.fetchNextItem()

    assert isinstance(item, Requests), f"""Expected type 'Tables.Requests' but got {
        type(item)})"""
    assert item.id == 1
