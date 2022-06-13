import http
import logging

import aioredis
import httpx
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from core import config
from core.logger import LOGGING
from db import elastic
from db import redis


app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о фильмах, жанрах и людях, участвовавших в создании кинопроизведений",
    version="1.0.0"
)


@app.on_event('startup')
async def statup():
    redis.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT),
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
        minsize=10,
        maxsize=20
    )
    elastic.es = AsyncElasticsearch(
        hosts=eval(config.ELASTICSEARCH_ADDRESS)
    )


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()


@app.middleware("http")
async def verify_token(request: Request, call_next):
    if request.headers['Authorization']:
        async with httpx.AsyncClient() as client:
            is_authorized = await client.post(
                f"http://{config.AUTH_APP}/login",
                headers={"Authorization": request.headers['Authorization']}
            )

        if is_authorized.status_code == http.HTTPStatus.ACCEPTED:
            response = await call_next(request)
        else:
            return ORJSONResponse(content={
                "message": "You need login for view films"
            }, status_code=401)
        
        return response
    else:
        return ORJSONResponse(content={
            "message": "we do not allow mobiles"
        }, status_code=401)


app.include_router(films.router, prefix='/api/v1/films')
app.include_router(genres.router, prefix='/api/v1/genres')
app.include_router(persons.router, prefix='/api/v1/persons')


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG
    )
