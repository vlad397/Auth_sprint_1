"""Models located here."""
# +не вижу значимых для проекта преимуществ наследования от одного класса
# по сравнению с множественным наследованием.

import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    """Timestamp base class."""

    created = models.DateTimeField(_('timestamp.created'), auto_now_add=True)
    modified = models.DateTimeField(_('timestamp.modified'), auto_now=True)

    class Meta(object):
        """Abstraction flag."""

        abstract = True


class UUIDMixin(models.Model):
    """Timestamp base class."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta(object):
        """Abstraction flag."""

        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    """Genre base class."""

    name = models.CharField(_('genre.name'), max_length=255)
    description = models.TextField(
        _('genre.description'),
        blank=True,
        null=True,
    )

    class Meta(object):
        """Metadata."""

        db_table = 'content\".\"genre'
        verbose_name = _('genre.meta.verbose_name')
        verbose_name_plural = _('genre.meta.verbose_name_plural')

    def __str__(self):
        """Get string repesentation (comment needed: PyDocstyle, D100).

        Returns:
            string representation of class instance
        """
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    """Person base class."""

    full_name = models.CharField(_('person.full_name'), max_length=255)
    birth_date = models.DateField(
        _('person.birth_date'),
        blank=True,
        default=None,
        null=True,
    )

    class Meta(object):
        """Metadata."""

        db_table = 'content\".\"person'
        verbose_name = _('person.meta.verbose_name')
        verbose_name_plural = _('person.meta.verbose_name_plural')

    def __str__(self):
        """Get string repesentation (comment needed: PyDocstyle, D100).

        Returns:
            string representation of class instance
        """
        return self.full_name


class GenreFilmwork(UUIDMixin):
    """GenreFilmwork base class."""

    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        """Metadata."""

        db_table = 'content\".\"genre_film_work'
        verbose_name = _('genre_film_work.meta.verbose_name')
        verbose_name_plural = _('genre_film_work.meta.verbose_name_plural')
        # тут не соглашусь, ударяясь в граммар-нацизм:
        # https://pypi.org/project/flake8-commas/ C819 вылезает
        # models.py:104:50: C819 trailing comma prohibited
        unique_together = (('film_work', 'genre'),)

    def __str__(self):
        """Get string repesentation (comment needed: PyDocstyle, D100).

        Returns:
            string representation of class instance
        """
        return ''  # review: not accepted, user has no need to see this key


class PersonFilmworkRoleChoices(models.TextChoices):
    """RoleChoices enum as class."""

    actor = 'actor', _('person_film_work.rolechoices.actor')
    director = 'director', _('person_film_work.rolechoices.director')
    writer = 'writer', _('person_film_work.rolechoices.writer')


class PersonFilmwork(UUIDMixin):
    """GenreFilmwork base class."""

    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        _('person_film_work.role'),
        max_length=8,
        choices=PersonFilmworkRoleChoices.choices,
        default=PersonFilmworkRoleChoices.actor,
        blank=False,
    )

    class Meta(object):
        """GenreFilmwork Metadata."""

        db_table = 'content\".\"person_film_work'
        verbose_name = _('person_film_work.meta.verbose_name')
        verbose_name_plural = _('person_film_work.meta.verbose_name_plural')
        unique_together = (('film_work', 'person', 'role'),)

    def __str__(self):
        """Get string repesentation (comment needed: PyDocstyle, D100).

        Returns:
            string representation of class instance
        """
        return ''  # review: not accepted, user has no need to see this key


class FilmworkTypeChoices(models.TextChoices):
    """FilmworkTypeChoices enum as class."""

    movie = 'movie', _('film_work.typechoices.movie')
    tv_show = 'tv_show', _('film_work.typechoices.tv_show')


class Filmwork(UUIDMixin, TimeStampedMixin):
    """Filmwork base class."""

    title = models.CharField(_('film_work.name'), max_length=255)
    description = models.TextField(
        _('film_work.description'),
        blank=True,
        null=True,
    )
    creation_date = models.DateField(
        _('film_work.creation_date'),
        blank=True,
        null=True,
    )
    rating = models.FloatField(
        _('film_work.rating'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    type = models.CharField(
        _('film_work.type'),
        max_length=7,
        choices=FilmworkTypeChoices.choices,
        default=FilmworkTypeChoices.movie,
        blank=False,
    )

    genres = models.ManyToManyField(
        Genre,
        through='GenreFilmwork',
    )
    persons = models.ManyToManyField(
        Person,
        through='PersonFilmwork',
    )

    certificate = models.CharField(
        _('film_work.certificate'),
        max_length=512,
        blank=True,
        null=True,
    )
    file_path = models.FileField(
        _('film_work.file'),
        blank=True,
        null=True,
        upload_to='movies/',
    )

    class Meta(object):
        """Filmwork metadata."""

        db_table = 'content\".\"film_work'
        verbose_name = _('film_work.meta.verbose_name')
        verbose_name_plural = _('film_work.meta.verbose_name_plural')

    def __str__(self):
        """Get string repesentation (comment needed: PyDocstyle, D100).

        Returns:
            string representation of class instance
        """
        return self.title
