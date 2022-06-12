import os

API_HOST = os.getenv('API_HOST', 'http://127.0.0.1:8000')
API_PATH_V1 = os.getenv('API_PATH_V1', '/api/v1/')

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 1))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'sDf8ad60d')

ELASTICSEARCH_ADDRESS = os.getenv(
    'ELASTICSEARCH_ADDRESS',
    '["http://localhost:9200"]'
)
