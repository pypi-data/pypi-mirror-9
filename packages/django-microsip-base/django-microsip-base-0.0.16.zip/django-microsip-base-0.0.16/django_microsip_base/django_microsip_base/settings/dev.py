from common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
MODO_SERVIDOR = 'PRUEBAS'
MICROSIP_VERSION = '2014'
EXTRA_MODULES = (
    # 'django-microsip-ventas-remgencargos',
    # 'django-microsip-cancela-cfdi',
    # 'django-microsip-consolidador',
    # 'microsip-liquida.django-microsip-liquida',
    # 'django_microsip_catalogoarticulos',
    # 'django_microsip_consultaprecio',
    # 'django_microsip_diot',
    # 'django_msp_cotizador',
    # 'django_msp_organizador',
    # 'django_sms',
    # 'django_msp_importa_inventario',
    # 'django_msp_polizas',
    # 'django-microsip-quickbooks',
    # 'django_microsip_exporta_xml',
    'django_msp_facturaglobal',
    # 'django_microsip_puntos',
    # 'django_sms',
    # 'django_microsip_catalogoprod',
    # 'django_msp_controldeacceso',
    # 'django_msp_inventarios',
    'djmicrosip_faexist',
    'django_microsip_exportaexcel',
)

EXTRA_MODULES = map(lambda app:'django_microsip_base.apps.plugins.%s.%s'%(app, app), EXTRA_MODULES)

from .common import get_microsip_extra_apps
MICROSIP_EXTRA_APPS, EXTRA_APPS = get_microsip_extra_apps(EXTRA_MODULES)
INSTALLED_APPS = DJANGO_APPS + MICROSIP_MODULES + MICROSIP_EXTRA_APPS

ROOT_URLCONF = 'django_microsip_base.urls.dev'

# Additional locations of static files
STATICFILES_DIRS = (
    (BASE_DIR + '/static/'),
)