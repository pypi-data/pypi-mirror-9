from django.conf import settings
MICROSIP_MODULES = settings.MICROSIP_MODULES
EXTRA_INFO = settings.EXTRA_INFO
EXTRA_MODULES = settings.EXTRA_MODULES
EXTRA_APPS = settings.EXTRA_APPS

from common import *
import os
import fdb
import sqlite3

TEST_DB = 'AD2007'
SYSDBA_PWD = '1'

DATABASE_ROUTERS = ['django_microsip_base.libs.databases_routers_tests.MainRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME':  os.path.join(BASE_DIR, 'data' ,'USERS.sqlite3'),
        'ATOMIC_REQUESTS': True,
    },
    'CONFIG': {
        'ENGINE': 'firebird', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'C:\Microsip datos\System\CONFIG.FDB',
        'TEST_NAME': 'C:\Microsip datos\System\\test_CONFIG.FDB',
        'USER': 'SYSDBA',                      # Not used with sqlite3.
        'PASSWORD': SYSDBA_PWD,                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3050',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS' : {'charset':'ISO8859_1'},
        'ATOMIC_REQUESTS': True,
    }
}

ROOT_URLCONF = 'django_microsip_base.urls.dev'
MICROSIP_VERSION = 2014
DATABASES[TEST_DB] = {
    'ENGINE': 'firebird', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': 'C:\Microsip datos\System\%s.FDB'%TEST_DB,
    'TEST_NAME': 'C:\Microsip datos\System\\test_%s.FDB'%TEST_DB,
    'USER': 'SYSDBA',                      # Not used with sqlite3.
    'PASSWORD': SYSDBA_PWD,                  # Not used with sqlite3.
    'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
    'PORT': '3050',                      # Set to empty string for default. Not used with sqlite3.
    'OPTIONS' : {'charset':'ISO8859_1'},
    'ATOMIC_REQUESTS': True,
}