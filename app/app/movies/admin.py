"""Register your models here."""
from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Gender admin registration."""

    list_display = ('name', 'description', 'created', 'modified')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Person admin registration."""

    list_display = ('full_name', 'created', 'modified')


class GenreFilmworkInline(admin.TabularInline):
    """GenreFilmwork admin registration."""

    extra = 0
    model = GenreFilmwork

    class Meta(object):
        """GenreFilmwork metadata."""

        verbose_name = 'Жанр кинопроизведения'
        verbose_name_plural = 'Жанры кинопроизведения'


class PersonFilmworkInline(admin.TabularInline):
    """PersonFilmwork admin registration."""

    extra = 0
    model = PersonFilmwork

    class Meta(object):
        """PersonFilmwork metadata."""

        verbose_name = 'Персона в кинопроизведении'
        verbose_name_plural = 'Персона в кинопроизведении'


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    """Filmwork admin registration."""

    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_display = (
        'title',
        'type',
        'creation_date',
        'rating',
        'created',
        'modified',
    )
    list_filter = ('type', 'rating', 'creation_date')
    search_fields = ('title', 'description')
