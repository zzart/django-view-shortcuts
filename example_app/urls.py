# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('example_app.views',
    url(r'^$', 'story_list', name='example-story-list'),
    url(r'^(?P<object_id>\d+)$', 'story_detail', name='example-story-detail'),
)
