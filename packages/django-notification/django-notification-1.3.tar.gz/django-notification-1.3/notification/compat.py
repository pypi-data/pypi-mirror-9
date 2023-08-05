import django

from django.conf import settings
from django.utils import six


# Django 1.5 add support for custom auth user model
if django.VERSION >= (1, 5):
    AUTH_USER_MODEL = settings.AUTH_USER_MODEL
else:
    AUTH_USER_MODEL = "auth.User"


def old_get_user_model():
    return User


try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = old_get_user_model

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote  # noqa

if six.PY3:
    from threading import get_ident
else:
    from thread import get_ident  # noqa
