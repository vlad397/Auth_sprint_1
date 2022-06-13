from enum import Enum
import os
from pathlib import Path
from logging import config as logging_config

from core.logger import LOGGING

from dotenv import load_dotenv
load_dotenv()

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv("PROJECT_NAME", 'movies')


REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 1))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

ELASTICSEARCH_ADDRESS = os.getenv(
    'ELASTICSEARCH_ADDRESS',
    '["http://localhost:9200"]'
)

AUTH_APP = os.getenv("AUTH_APP", "auth")

BASE_DIR = Path(__file__).parent.parent
