from django.conf.urls.defaults import *
from django_jsonrpc import jsonrpc_site

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from plugins.models import PluginVersion, Plugin
from application.models import AppVersion, App


admin.autodiscover()
admin.site.register(AppVersion)
admin.site.register(App)


urlpatterns = patterns('',
    # Example:
    # (r'^plugin_repository/', include('plugin_repository.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    url(r'^json/browse/$', 'django_jsonrpc.views.browse', name='jsonrpc_browser'),
    url(r'^json/$', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),
    (r'^json/(?P<method>[a-zA-Z0-9.-_]+)$', jsonrpc_site.dispatch),

    (r'^plugins/', include('plugins.urls')),
    (r'^application/', include('application.urls'))
)
