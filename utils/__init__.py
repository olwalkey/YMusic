from .db import interactions
from alembic.config import Config
from alembic import command


from .config import config

alembic_cfg = Config()
alembic_cfg.set_main_option("script_location", "utils/alembic")
alembic_cfg.set_main_option("prepend_sys_path", ".")
alembic_cfg.set_main_option("sqlalchemy.url", f'postgresql://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.db}')

command.upgrade(alembic_cfg, "head")

interaction = interactions()
interaction._connect()

from .downloader import Downloader  # type: ignore

youtube = Downloader()
