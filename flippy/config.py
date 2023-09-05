import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from flippy.backends import DjangoBackend

logger = logging.getLogger(__name__)

# get class
try:
    _backend = settings.FLIPPY_BACKEND
    logger.debug('Flippy backend found in settings: "%s"', _backend)

    # get a class from the string
    try:
        if '.' not in _backend:
            logger.debug('Assuming this is a built-in backend')
            _backend = f'flippy.backends.{_backend}'
        _class = import_string(_backend)

    except ImportError:
        raise ImproperlyConfigured(
            f"Backend `{_backend}` was not found; try passing a fully-qualified path as a dotted string."
        )

except AttributeError:
    # default if nothing is configured
    logger.debug('Did not find FLIPPY_BACKEND in settings; defaulting to DjangoBackend')
    _class = DjangoBackend

# check for settings
try:
    _args = settings.FLIPPY_ARGS
except AttributeError:
    logger.debug('No FLIPPY_ARGS found in settings; defaulting to empty list')
    _args = []

# build it
if isinstance(_args, (list, tuple)):
    flippy_backend = _class(*_args)
elif isinstance(_args, dict):
    flippy_backend = _class(**_args)
elif isinstance(_args, str):
    flippy_backend = _class(_args)
else:
    logger.warn("settings.FLIPPY_ARGS had content, but it wasn't a list, tuple, dict, or str")
    flippy_backend = _class()
