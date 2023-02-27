import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleType(models.TextChoices):
    """Class to add role choices."""

    actor = 'actor', _('actor')
    writer = 'writer', _('writer')
    director = 'director', _('director')


class FilmTypeChoices(models.TextChoices):
    """Class to add filmwork type choices."""

    movie = 'movie', 'MOVIE'
    tv_show = 'tv_show', 'TV SHOW'


class ModifiedMixin(models.Model):
    modified = models.BooleanField(default=True, null=True)

    def __init__(self, *args, **kwargs):
        super(ModifiedMixin, self).__init__(*args, **kwargs)
        self.last_modified_state = self.modified

    def save(self, *args, **kwargs):
        if self.last_modified_state == self.modified:
            self.modified = True
        super().save(*args, **kwargs)
        self.last_modified_state = self.modified

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    """Basic class for created and modified fields."""

    created_at = models.DateTimeField(_('created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modified'), auto_now=True)

    class Meta(object):
        """Parent class is abstract."""

        abstract = True


class UUIDMixin(models.Model):
    """Basic class for id(uuid) field."""

    id = models.UUIDField(
        _('id'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta(object):
        """Parent class is abstract."""

        abstract = True


class Person(UUIDMixin, TimeStampedMixin, ModifiedMixin):
    """Person class."""

    full_name_max_len = 50
    full_name = models.CharField(
        _('full_name'),
        max_length=full_name_max_len,
        blank=False,
    )

    class Meta(object):
        """Django metaclass for Person."""

        db_table = 'content\".\"person'
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'

    def __str__(self):
        """
        Person str output.

        Returns:
            str as the full_name
        """
        return self.full_name


class Genre(UUIDMixin, TimeStampedMixin):
    """Genre class."""

    name_max_len = 255

    name = models.CharField(_('name'), max_length=name_max_len)
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta(object):
        """Django meta class for Genre."""

        db_table = 'content\".\"genre'
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        """
        Genre str output.

        Returns:
            str as the name
        """
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin, ModifiedMixin):
    """Filmwork class."""

    title_max_len = 255
    type_max_len = 40

    file_path = models.FileField(
        _('file'),
        blank=True,
        null=True,
        upload_to='movies/',
    )
    title = models.CharField(
        _('title'),
        max_length=title_max_len,
        blank=False,
    )
    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
    )
    creation_date = models.DateField(
        _('creation_date'),
        blank=True,
        null=True,
    )
    rating = models.FloatField(
        _('rating'),
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        null=True,
    )
    type = models.CharField(
        _('type'),
        choices=FilmTypeChoices.choices,
        default=FilmTypeChoices.movie,
        max_length=type_max_len,
    )
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta(object):
        """Django meta class for FilmWork."""

        db_table = 'content\".\"film_work'
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'
        indexes = [
            models.Index(fields=['creation_date'], name='film_work_creation_date_idx'),
        ]

    def __str__(self):
        """
        Filmwork str output.

        Returns:
            str as the title
        """
        return self.title


class GenreFilmwork(UUIDMixin):
    """Genre and filmwork connection table."""

    film_work = models.ForeignKey(
        Filmwork,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name=_('genre'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        """Django metalass for genre and filmwork connection."""

        db_table = 'content\".\"genre_film_work'
        verbose_name = 'Жанр кинопроизведения'
        verbose_name_plural = 'Жанры кинопроизведения'


class PersonFilmwork(UUIDMixin):
    """Person and filmwork connection table."""

    role_max_len = 50

    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name=_('person'),
    )
    role = models.CharField(_('role'), max_length=role_max_len, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        """Django metaclass for person and film work connection."""

        db_table = 'content\".\"person_film_work'
        verbose_name = 'Участик кинопроизведения'
        verbose_name_plural = 'Участники кинопроизведения'

        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person'], name='film_work_person_idx'),
        ]

    def __str__(self):
        """
        Person AND FilmWork connection str output.

        Returns:
            str as the 'Person: person.__str__()
            Role: role.__str__()
            Film: film_work.__str__()'
        """
        return 'Person: {0} Role: {1} Film:{2}'.format(
            self.person,
            self.role,
            self.film_work,
        )
