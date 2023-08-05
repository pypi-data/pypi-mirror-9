from django.conf.urls import patterns, url

from .provider import InterSISProvider

urlpatterns = patterns(InterSISProvider.package + '.views',
                       url('^login/$', 'oauth2_login', name=InterSISProvider.id + "_login"),
                       url('^login/callback/$', 'oauth2_callback', name=InterSISProvider.id + "_callback"))
