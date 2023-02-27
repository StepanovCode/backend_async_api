from typing import Optional

from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str]


class Person(BaseModel):
    id: str
    name: str


class Writer(Person):
    ...


class Actor(Person):
    ...


class FilmWork(BaseModel):

    id: str
    title: str
    description: Optional[str] = ""
    genre: list[str]
    imdb_rating: Optional[float] = 0.0

    actors: list[Actor]
    actors_names: list[str]
    writers: list[Writer]
    writers_names: list[str]
    director: str
