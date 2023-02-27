"""Dataclasses for models, which work with sql."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

strftime_format = '%Y-%m-%d %H:%M:%S.%f+00'


@dataclass
class FilmWork:
    title: str
    type: str
    id: uuid.UUID = field(default=uuid.uuid4)
    creation_date: str = field(default=None)
    file_path: str = field(default=None)
    description: str = field(default=None)
    rating: float = field(default=0.0)
    created_at: str = field(default=datetime.utcnow().strftime(strftime_format))
    updated_at: str = field(default=datetime.utcnow().strftime(strftime_format))


@dataclass
class Genre:
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    description: str = field(default=None)
    created_at: str = field(default=datetime.utcnow().strftime(strftime_format))
    updated_at: str = field(default=datetime.utcnow().strftime(strftime_format))


@dataclass
class GenreFilmWork:
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: str = field(default=datetime.utcnow().strftime(strftime_format))


@dataclass
class Person:
    full_name: str
    created_at: str = field(default=datetime.utcnow().strftime(strftime_format))
    updated_at: str = field(default=datetime.utcnow().strftime(strftime_format))
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmWork:
    film_work_id: str
    person_id: str
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: str = field(default=datetime.utcnow().strftime(strftime_format))


switch_to_dataclass_by_table_name = {
    'film_work': FilmWork,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmWork,
    'person_film_work': PersonFilmWork,
}
