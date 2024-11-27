from .db import interactions, DBInfo
from alembic.config import Config
from alembic import command
from robyn import Robyn
from .config import config
from loguru import logger

#from .downloader import Downloader, robyn

def migrateDb(
    engineType: DBInfo,
    username: str = config.db.user,
    password: str = config.db.password,
    host: str = config.db.host,
    port: int = config.db.port,
    database: str = config.db.db
) -> int:
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "utils/alembic")
    alembic_cfg.set_main_option("prepend_sys_path", ".")
    if not engineType['database'] == "sqlite":
        alembic_cfg.set_main_option("sqlalchemy.url", f'{engineType["database"]}://{username}:{password}@{host}:{port}/{database}')
    else:
        alembic_cfg.set_main_option("sqlalchemy.url", f'{engineType["database"]}:///{database}')

    try:
        command.ensure_version(alembic_cfg)
        command.upgrade(alembic_cfg, "head")
        return 1
    except Exception as e:
        logger.error(e)
        return 0

#interaction = interactions()
#interaction.connect()



#def initapp(app: Robyn):
    #robyn(app)


#youtube = Downloader()
