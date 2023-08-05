from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'tethys_datasets.views.home', name='home'),
)