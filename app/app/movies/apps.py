"""Separate config for apps."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MoviesConfig(AppConfig):
    """Basic movies app config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'
    verbose_name = _('app.verbose_name')
