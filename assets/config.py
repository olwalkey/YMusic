from typing import List, Optional
from pydantic import BaseModel, ValidationError
import yaml, sys
from loguru import logger
from munch import munchify




class DbConfig(BaseModel):
  host: str
  port: int
  db: str
  user: str
  password: str

class AppConfig(BaseModel):
  host: str
  port: int
  user: str
  password: str
  debug: bool
  ratelimit: Optional[int]
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