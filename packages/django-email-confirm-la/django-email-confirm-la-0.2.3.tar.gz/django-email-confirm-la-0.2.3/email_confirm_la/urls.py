# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'email_confirm_la.views',
    url(r'^key/(?P<confirmation_key>\w+)/$', 'confirm_email', name='confirm_email'),
)
