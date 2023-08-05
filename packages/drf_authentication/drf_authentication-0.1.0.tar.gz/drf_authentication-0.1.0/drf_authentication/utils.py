__author__ = 'cenk'


def get_user_model():
    try:
        from django.contrib.auth import get_user_model

        User = get_user_model()
    except ImportError:  # Django < 1.5
        from django.contrib.auth.models import User

    return User