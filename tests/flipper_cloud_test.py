import pytest

pytestmark = pytest.mark.flippercloud

from os import environ

from flippy.backends import FlipperCloudBackend
from flippy.core import BaseBackend
from tests.backend_shared import *

try:
    TOKEN = environ['FLIPPER_CLOUD_TOKEN']
except KeyError:
    TOKEN = None


@pytest.fixture
def backend() -> BaseBackend:
    if not TOKEN:
        raise pytest.UsageError('FLIPPER_CLOUD_TOKEN must be set in the environment')
    return FlipperCloudBackend(TOKEN)


# TEST_FEATURE comes from backend_shared

def teardown_module():
    backend = FlipperCloudBackend(TOKEN)
    for f in backend.features():
        if f.startswith(TEST_FEATURE):
            backend.remove(f)
