from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from flippy.backends import DjangoBackend


try:
    _backend = settings.FLIPPY_BACKEND

    # get a class from the string
    try:
        if '.' not in _backend:
            _backend = f'flippy.backends.{_backend}'
        _class = import_string(_backend)
    except ImportError:
        raise ImproperlyConfigured(
            f"Backend `{_backend}` was not found; try passing a fully-qualified path."
        )

    # instantiate (TODO: with correct parameters)
    flippy_backend = _class()

except AttributeError:
    flippy_backend = DjangoBackend()
