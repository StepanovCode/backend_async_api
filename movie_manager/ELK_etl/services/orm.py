import os

import django
from django.db.models import QuerySet
from models import pydentic_models
from utils.decorators import backoff

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup(set_prefix=False)

from movies.models import Filmwork, Genre, Person


class BasicQueries:
    @staticmethod
    @backoff()
    def get_filmwork_with_prefetch_related():
        return Filmwork.objects.prefetch_related("persons", "genres")

    @staticmethod
    @backoff()
    def get_genres():
        return Genre.objects

    @staticmethod
    @backoff()
    def get_persons():
        return Person.objects


class PersonService:
    @staticmethod
    def prepare_pydantic(person: Person):
        _person = pydentic_models.Person(
            id=str(person.id),
            name=person.full_name
        )
        return _person


class GenreService:
    @staticmethod
    def prepare_pydantic(genre: Genre):
        _genre = pydentic_models.Genre(
            id=str(genre.id),
            name=genre.name,
            description=genre.description
        )
        return _genre


class FilmworkService:
    @staticmethod
    @backoff()
    def mark_as_done(filmwork_query: QuerySet):
        Filmwork.objects.filter(id__in=filmwork_query).update(modified=False)

    @staticmethod
    @backoff()
    def prepare_pydantic_filmwork(filmwork: Filmwork):
        actors = filmwork.persons.filter(personfilmwork__role="actor").order_by(
            "full_name"
        )
        actors_names_list = [actor.full_name for actor in actors]

        writers = filmwork.persons.filter(personfilmwork__role="writer").order_by(
            "full_name"
        )
        writers_names_list = [writer.full_name for writer in writers]

        directors = filmwork.persons.filter(personfilmwork__role="director").order_by(
            "full_name"
        )
        directors_names = ", ".join([director.full_name for director in directors])

        actors = [
            pydentic_models.Actor(id=str(actor.id), name=actor.full_name)
            for actor in actors
        ]
        writers = [
            pydentic_models.Writer(id=str(writer.id), name=writer.full_name)
            for writer in writers
        ]

        genres = filmwork.genres.order_by("name")
        genre_name_list = [genre.name for genre in genres]

        _film = pydentic_models.FilmWork(
            id=str(filmwork.id),
            title=filmwork.title,
            description=filmwork.description,
            genre=genre_name_list,
            imdb_rating=filmwork.rating,
            actors=actors,
            actors_names=actors_names_list,
            writers=writers,
            writers_names=writers_names_list,
            director=directors_names,
        )
        return _film
