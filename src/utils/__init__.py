from src.database.migrate import migrateDb
from src.downloader import robyn

from robyn import Robyn


def initapp(app: Robyn):
    migrateDb()
    robyn(app)




