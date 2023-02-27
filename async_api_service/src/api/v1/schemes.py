from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    title: str | None
    description: str | None
    imdb_rating: float | None
    actors: list[Person] | None
    writers: list[Person] | None
    actors_names: list[str] | None
    director: list[str] | str | None
    writers_names: list[str] | None
    genre: list[str] | None


class Genre(BaseModel):
    id: str
    name: str
