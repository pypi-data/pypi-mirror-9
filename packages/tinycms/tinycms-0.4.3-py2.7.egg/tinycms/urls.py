from django.conf.urls import patterns, include, url
from django.conf import settings

from views import *


urlpatterns = patterns('',
    #url(r'^$', show_page),
    url(r'^(?P<url>.*)$', show_page,name="tinycms_show_page"),
)
