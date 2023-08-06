# coding=utf-8
from __future__ import absolute_import, unicode_literals
from django.conf.urls import patterns, url, include

urlpatterns = patterns(
    '',
    url(r'^mail/', include('mail_confirmation.urls'
                           , namespace='mail_confirmation')),

)
