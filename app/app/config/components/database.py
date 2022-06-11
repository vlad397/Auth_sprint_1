"""Настройки БД для django."""

import os
import types

DATABASES = types.MappingProxyType({
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            # Нужно явно указать схемы, с которыми будет работать приложение.
            'options': '-c search_path=public,content',
        },
    },
})
