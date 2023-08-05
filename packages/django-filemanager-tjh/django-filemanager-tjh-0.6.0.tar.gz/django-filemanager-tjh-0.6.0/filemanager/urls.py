from django.conf.urls import patterns, url, include

urlpatterns = patterns(
    'filemanager.views',
    url(r'^$', 'handler', name='filemanager'),
)
