import os
from pathlib import Path

import dj_database_url
from decouple import config

try:
    TOKEN = os.environ['TOKEN']
    DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'])}

except KeyError:
    TOKEN = config('TOKEN')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': '5432',
        },
        'state': {
            'NAME': config('STATE_DB_NAME'),
            'HOST': config('STATE_HOST'),
            'PORT': config('STATE_PORT'),
            'USERNAME': config('STATE_USER'),
            'PASSWORD': config('STATE_PASSWORD'),
        }
    }


BASE_DIR = Path(__file__).resolve().parent.parent
