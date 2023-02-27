from http import HTTPStatus

from api.v1 import get_raw_path
from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from messages.exceptions import messages
from services.genres import GenreService, get_genre_service

from .schemes import Genre

router = APIRouter()


@router.get('/{genre_id}',
            description=settings.OPENAPI_GET_GENRE_DESCRIPTION,
            response_model=Genre)
async def get_genre_by_uuid(
        request: Request,
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)) -> Genre:

    genre = await genre_service.get_by_id(get_raw_path(request), genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return genre


@router.get('/',
            description=settings.OPENAPI_GET_GENRES_DESCRIPTION,
            response_model=list[Genre])
async def get_genres_list(
        request: Request,
        size: int = Query(default=50, alias='page[size]', description=settings.OPENAPI_SIZE_PARAMETER),
        number: int = Query(default=1, alias='page[number]', description=settings.OPENAPI_NUMBER_PARAMETER),
        sort: str | None = Query(default=None, description=settings.OPENAPI_SORT_PARAMETER),
        genre_service: GenreService = Depends(get_genre_service)) -> list[Genre]:

    elements = await genre_service.get_all(get_raw_path(request), number, size, sort)
    if not elements:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return elements


@router.get('/search/',
            description=settings.OPENAPI_SEARCH_GENRES_DESCRIPTION,
            response_model=list[Genre])
async def get_genres_list_search(
        request: Request,
        size: int = Query(default=50, alias='page[size]', description=settings.OPENAPI_SIZE_PARAMETER),
        number: int = Query(default=1, alias='page[number]', description=settings.OPENAPI_NUMBER_PARAMETER),
        sort: str | None = Query(default=None, description=settings.OPENAPI_SORT_PARAMETER),
        search: str = Query(default='', description=settings.OPENAPI_SEARCH_PARAMETER),
        genre_service: GenreService = Depends(get_genre_service)) -> list[Genre]:

    elements = await genre_service.get_all(get_raw_path(request), number, size, sort, search)
    if not elements:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return elements
