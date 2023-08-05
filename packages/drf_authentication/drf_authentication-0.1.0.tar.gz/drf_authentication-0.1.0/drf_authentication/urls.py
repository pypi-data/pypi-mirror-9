from django.conf.urls import patterns, url

from drf_authentication.views.drf_auth_login import DrfAuthLogin
from drf_authentication.views.simple_static_view import SimpleStaticView


__author__ = 'cenk'

urlpatterns = patterns('',
                       url(r'^$', SimpleStaticView.as_view(), name='drf_auth_index'),
                       url(r'^auth/(?P<api>login)/$', DrfAuthLogin.as_view(), name='drf_login'),

)