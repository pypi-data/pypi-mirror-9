from django.conf.urls import patterns, url

urlpatterns = patterns('mediagenie.views',
    url(r'^(?P<path>.*)$', 'dev_media')
)
