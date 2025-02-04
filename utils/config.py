from typing import Optional
from pydantic import BaseModel, ValidationError
import yaml
import sys
from loguru import logger


class DbConfig(BaseModel):
    engine: str
    host: str
    port: int
    db: str
    user: str
    password: str
    timezone: str


class AppConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    debug: bool
    trace: bool
    ratelimit: int
    restrictfilenames: bool
    # dbScanRate: int
    db: DbConfig


def load_config(file_path: str) -> AppConfig:
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
        try:
            return AppConfig(**yaml_data)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")


file_path = 'config.yaml'
try:
    config = load_config(file_path)
except ValueError as e:
    logger.error(e)
    sys.exit(0)
