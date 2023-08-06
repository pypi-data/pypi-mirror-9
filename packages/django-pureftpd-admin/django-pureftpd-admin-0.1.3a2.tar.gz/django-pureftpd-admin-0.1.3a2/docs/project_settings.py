__author__ = 'ivan'

from pureftpd_admin.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'pureftpd',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'pureftpd',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

USE_X_FORWARDED_HOST = True
STATIC_URL = '/pureftpd_admin/static/'
STATIC_ROOT = '/pureftpd-admin/files/static'
MEDIA_URL = '/pureftpd_admin/media/'
MEDIA_ROOT = '/pureftpd-admin/files/media'

FTPUSERS_DEFAULT_UID = 81
FTPUSERS_DEFAULT_GID = 81
FTPUSERS_ROOT_PATH = '/www'