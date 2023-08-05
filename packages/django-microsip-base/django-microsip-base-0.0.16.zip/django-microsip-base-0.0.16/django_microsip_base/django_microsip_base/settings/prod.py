from common import *
import os

DEBUG = False
ALLOWED_HOSTS = ['*',]
TEMPLATE_DEBUG = DEBUG
MODO_SERVIDOR = 'PROD'

extra_list = os.environ['SIC_INSTALLED_APPS'].split(',')
extra_list.remove('')
EXTRA_MODULES = tuple(extra_list)

MICROSIP_VERSION = os.environ['MICROSIP_VERSION']

from .common import get_microsip_extra_apps
MICROSIP_EXTRA_APPS, EXTRA_APPS = get_microsip_extra_apps(EXTRA_MODULES)
    
INSTALLED_APPS = DJANGO_APPS + MICROSIP_MODULES + MICROSIP_EXTRA_APPS

ROOT_URLCONF = 'django_microsip_base.urls.prod'

# Additional locations of static files
STATICFILES_DIRS = (
    (BASE_DIR + '/static/'),
)