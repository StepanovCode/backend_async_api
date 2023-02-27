from http import HTTPStatus

from api.v1 import get_raw_path
from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from messages.exceptions import messages
from services.person import PersonService, get_person_service

from .schemes import Person

router = APIRouter()


@router.get('/{person_id}',
            description=settings.OPENAPI_GET_PERSON_DESCRIPTION,
            response_model=Person)
async def get_person_by_uuid(
        request: Request,
        person_id: str,
        person_service: PersonService = Depends(get_person_service)) -> Person:

    person = await person_service.get_by_id(get_raw_path(request), person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return person


@router.get('/',
            description=settings.OPENAPI_GET_PERSONS_DESCRIPTION,
            response_model=list[Person])
async def get_persons_list(
        request: Request,
        size: int = Query(default=50, alias='page[size]', description=settings.OPENAPI_SIZE_PARAMETER),
        number: int = Query(default=1, alias='page[number]', description=settings.OPENAPI_NUMBER_PARAMETER),
        sort: str | None = Query(default=None, description=settings.OPENAPI_SORT_PARAMETER),
        person_service: PersonService = Depends(get_person_service)) -> list[Person]:

    elements = await person_service.get_all(get_raw_path(request), number, size, sort)
    if not elements:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return elements


@router.get('/search/',
            description=settings.OPENAPI_SEARCH_PERSONS_DESCRIPTION,
            response_model=list[Person])
async def get_persons_list_search(
        request: Request,
        size: int = Query(default=50, alias='page[size]', description=settings.OPENAPI_SIZE_PARAMETER),
        number: int = Query(default=1, alias='page[number]', description=settings.OPENAPI_NUMBER_PARAMETER),
        sort: str | None = Query(default=None, description=settings.OPENAPI_SORT_PARAMETER),
        search: str = Query(default='', description=settings.OPENAPI_SEARCH_PARAMETER),
        person_service: PersonService = Depends(get_person_service)) -> list[Person]:

    elements = await person_service.get_all(get_raw_path(request), number, size, sort, search)
    if not elements:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.NOT_FOUND)
    return elements
