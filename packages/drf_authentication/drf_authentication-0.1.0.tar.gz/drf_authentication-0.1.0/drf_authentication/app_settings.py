from __future__ import unicode_literals

from django.conf import settings

from drf_authentication.serializers.drf_auth_login_serializer import DrfAuthLoginSerializer
from drf_authentication.serializers.drf_auth_user_serializer import DrfAuthUserSerializer


__author__ = 'cenk'
# TODO
AUTHENTICATION_BACKEND_TYPES = (
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    'drf_angular_auth.backends.basic_authentication.BasicAuthentication',
    'drf_angular_auth.backends.basic_authentication.SessionAuthentication',
    'drf_angular_auth.backends.basic_authentication.TokenAuthentication',

)

USER_SETTINGS = getattr(settings, 'DRF_AUTH', None)

DEFAULTS = {
    'LOGIN_SERIALIZER': DrfAuthLoginSerializer,
    'USER_SERIALIZER': DrfAuthUserSerializer,
    'AUTHENTICATION_BACKENDS': settings.AUTHENTICATION_BACKENDS

}


class APISettings(object):
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from rest_framework.settings import api_settings
        print(api_settings.DEFAULT_RENDERER_CLASSES)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS


    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        setattr(self, attr, val)
        return val


api_settings = APISettings(USER_SETTINGS, DEFAULTS)