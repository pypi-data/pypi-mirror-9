from django.conf.urls.defaults import patterns

import views
import app_settings

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    (r'^latest/(?P<package_name>[^\/]+)/$', views.redirect_to_latest),
    (r'^data/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': app_settings.DATA_DIR,
                    'show_indexes': True}),
)
