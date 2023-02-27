from .base import BaseOrjsonModel
from .person import Person


class Film(BaseOrjsonModel):
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
