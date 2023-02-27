from http import HTTPStatus

from api.v1 import get_raw_path
from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from messages.exceptions import messages
from services.film import FilmService, get_film_service

from .schemes import Film

router = APIRouter()


@router.get('/{film_id}',
            description=settings.OPENAPI_GET_FILM_DESCRIPTION,
            response_model=Film)
async def get_film_by_uuid(
        request: Request,
        film_id: str,
        film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(get_raw_path(request), film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return film


@router.get('/',
            description=settings.OPENAPI_GET_FILMS_DESCRIPTION,
            response_model=list[Film])
async def get_films_list(
        request: Request,
        size: int = Query(default=50, alias='page[size]', description=settings.OPENAPI_SIZE_PARAMETER),
        number: int = Query(default=1, alias='page[number]', description=settings.OPENAPI_NUMBER_PARAMETER),
        sort: str | None = Query(default='-imdb_rating', description=settings.OPENAPI_SORT_PARAMETER),
        filter_genre: str = Query(default='', alias='filter[genre]', description=settings.OPENAPI_FILTER_PARAMETER),
        film_service: FilmService = Depends(get_film_service)) -> list[Film]:

    elements = await film_service.get_all(get_raw_path(request), number, size, sort, filter_=filter_genre)
    if not elements:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return elements


@router.get('/search/',
            description=settings.OPENAPI_SEARCH_FILMS_DESCRIPTION,
            response_model=list[Film])
async def get_films_list_search(
        request: Request,
        size: int = Query(default=50, alias='page[size]', description=settings.OPENAPI_SIZE_PARAMETER),
        number: int = Query(default=1, alias='page[number]', description=settings.OPENAPI_NUMBER_PARAMETER),
        sort: str = Query(default='-imdb_rating', description=settings.OPENAPI_SORT_PARAMETER),
        filter_genre: str | None = Query(
            default=None, alias='filter[genre]', description=settings.OPENAPI_FILTER_PARAMETER
        ),
        search: str = Query(default='', description=settings.OPENAPI_SEARCH_PARAMETER),
        film_service: FilmService = Depends(get_film_service)) -> list[Film]:

    elements = await film_service.get_all(get_raw_path(request), number, size, sort, search, filter_=filter_genre)
    if not elements:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return elements
