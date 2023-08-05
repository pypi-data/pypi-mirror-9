from __future__ import absolute_import
from .base import *

SECRET_KEY = '!^9c1e&n8gj6ps2&1z@wr-8xf_91jy21=8j77ksi*lgh!l+d0p'

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME': 'mayan',
        'USER': 'root',
        'PASSWORD': '584853069',
        #'HOST': '127.0.0.1',
        #'PORT': '5432',
     }
}

