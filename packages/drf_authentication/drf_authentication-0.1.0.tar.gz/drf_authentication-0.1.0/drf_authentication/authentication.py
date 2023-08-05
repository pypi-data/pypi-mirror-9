import inspect
import re

from django.contrib.auth import user_login_failed
from django.core.exceptions import ImproperlyConfigured, PermissionDenied


try:
    from django.utils.module_loading import import_string

    import_settings = import_string
except:
    # django < 1.7
    from django.utils.module_loading import import_by_path

    import_settings = import_by_path

from drf_authentication.app_settings import api_settings


__author__ = 'cenk'


def _clean_credentials(credentials):
    """
    Cleans a dictionary of credentials of potentially sensitive info before
    sending to less secure functions.

    Not comprehensive - intended for user_login_failed signal
    """
    SENSITIVE_CREDENTIALS = re.compile('api|token|key|secret|password|signature', re.I)
    CLEANSED_SUBSTITUTE = '********************'
    for key in credentials:
        if SENSITIVE_CREDENTIALS.search(key):
            credentials[key] = CLEANSED_SUBSTITUTE
    return credentials


def load_backend(path):
    return import_settings(path)()


def get_backends():
    backends = []
    for backend_path in api_settings.AUTHENTICATION_BACKENDS:
        backends.append(load_backend(backend_path))
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does AUTHENTICATION_BACKENDS contain anything?')
    return backends


def authenticate(**credentials):
    """
    If the given credentials are valid, return a User object.
    """
    for backend in get_backends():
        try:
            inspect.getcallargs(backend.authenticate, **credentials)
        except TypeError:
            # This backend doesn't accept these credentials as arguments. Try the next one.
            continue

        try:
            user = backend.authenticate(**credentials)
        except PermissionDenied:
            # This backend says to stop in our tracks - this user should not be allowed in at all.
            return None
        if user is None:
            continue
        # Annotate the user object with the path of the backend.
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user

    # The credentials supplied are invalid to all backends, fire signal
    user_login_failed.send(sender=__name__,
                           credentials=_clean_credentials(credentials))