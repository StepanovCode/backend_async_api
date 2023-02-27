import json

import uvicorn
from fastapi.exceptions import RequestValidationError

from api.v1 import films, genres, persons
from core.config import settings
from db import search_engine, storage
from db.search_engine import ElasticSearchEngine
from db.storage import RedisStorage
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION

)

storage: RedisStorage
search_engine: ElasticSearchEngine


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return ORJSONResponse({'error': str(exc)}, status_code=400)


@app.on_event('startup')
async def startup():
    global search_engine, storage

    search_engine = ElasticSearchEngine(settings.ELASTIC_HOST, settings.ELASTIC_PORT)
    await search_engine.create_connection()

    storage = RedisStorage(host=settings.REDIS_HOST,
                           port=settings.REDIS_PORT,
                           password=settings.REDIS_PASSWORD)
    await storage.create_connection()


@app.on_event('shutdown')
async def shutdown():
    await storage.close()
    await search_engine.close()


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8200,
    )
