import autocomplete_light
autocomplete_light.autodiscover()

from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.conf import settings

urlpatterns = patterns('',
    #main
    url(r'', include('django_microsip_base.apps.main.urls', namespace='main')),
    url(r'', include('microsip_api.apps.config.urls', namespace='config')),
    url(r'administrador/', include('microsip_api.apps.administrador.urls', namespace='administrador')),
    url(r'autocomplete/', include('autocomplete_light.urls')),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',
		{'document_root':settings.MEDIA_ROOT,}
	),
)
for plugin in settings.EXTRA_APPS:
    urlpatterns += url('^'+plugin['url_main_path'], include(plugin['app']+'.urls', namespace= plugin['url_main_path'])),


urlpatterns += staticfiles_urlpatterns()