# -*- coding:utf-8 -*-
"""urls"""

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^djaloha/aloha-config.js', 'djaloha.views.aloha_init', name='aloha_init'),
)
