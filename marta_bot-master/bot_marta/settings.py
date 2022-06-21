import os
from pathlib import Path

import dj_database_url
from decouple import config

try:
    # Вытаскивает токен и базыданных из переменной окружения
    TOKEN = os.environ['TOKEN']
    DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'])}

except KeyError:
    # Запускается при условии: не нашлись в переменной окружения токен и базы данных
    # Создаем токен
    TOKEN = config('TOKEN')
    # Создание словаря базы данных
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
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

<<<<<<< HEAD

BASE_DIR = Path(__file__).resolve().parent.parent.parent
=======
# Определяет папку родителя родителя для файла, из которого был отправлен запрос
BASE_DIR = Path(__file__).resolve().parent.parent
>>>>>>> 554ba25e9dfbe0553a3b2ea45ebe2dad29d2fc6e
