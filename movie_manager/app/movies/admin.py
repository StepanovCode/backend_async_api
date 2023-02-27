from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Genre admin panel setting."""

    list_display = ('name', 'description', 'created_at', 'updated_at')


class GenreFilmworkInline(admin.TabularInline):
    """Genre with FilmWork connection TabularInline admin panel."""

    model = GenreFilmwork


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Person admin panel setting."""

    list_display = ('full_name', 'created_at', 'updated_at')


class PersonFilmworkInline(admin.TabularInline):
    """Person with FilmWork connection TabulaerInline admin panel."""

    model = PersonFilmwork


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    """FilmWork admin panel setting."""

    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_display = (
        'title',
        'type',
        'creation_date',
        'rating',
        'created_at',
        'updated_at',
    )
    list_filter = ('type',)
    search_fields = ('title', 'description', 'id')
