"""Separate file for config vars."""

import os

# принято, исправлено: не будем мелочиться на возможные "On" и "да"
# при этом, исправлено на set; на заметку: https://flake8.codes/WPS510/
DEBUG = os.environ.get('DEBUG', 'False') in {'1', 'True', 'true'}
