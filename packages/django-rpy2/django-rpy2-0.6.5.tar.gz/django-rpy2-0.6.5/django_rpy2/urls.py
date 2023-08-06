try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from .views import *


urlpatterns = patterns('',
#  url(r'^$',                   Scripts(), name="charts"),
#  url(r'^(?P<slug>[\w-]+)/$',  Script(), name="chart"),
)

