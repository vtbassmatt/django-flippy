import pytest
pytestmark = pytest.mark.flippercloud

from os import environ

from flippy.backends import FlipperCloudBackend
from flippy.core import BaseBackend, Gate


try:
    TOKEN = environ['FLIPPER_CLOUD_TOKEN']
except KeyError:
    TOKEN = None

if not TOKEN:
    raise pytest.UsageError('FLIPPER_CLOUD_TOKEN must be set in the environment')


@pytest.fixture
def backend() -> BaseBackend:
    return FlipperCloudBackend(TOKEN)


# NOTE! Only create features with the prefix listed here. That way our teardown
# will (attempt to) clean up after itself. Like this:
# my_name = f"{TEST_FEATURE}_foo"
#
# Also, be sure to use a new feature name in each testcase to keep them isolated.
TEST_FEATURE = 'django_flippy_testcase'

def teardown_module():
    backend = FlipperCloudBackend(TOKEN)
    for f in backend.features():
        if f.startswith(TEST_FEATURE):
            backend.remove(f)


def test_add_feature(backend: BaseBackend):
    assert backend.add(f'{TEST_FEATURE}_one') == True


def test_feature_defaults_off(backend: BaseBackend):
    feature_name = f'{TEST_FEATURE}_two'
    backend.add(feature_name)
    f = backend.get(feature_name)
    assert f.state == 'off'


def test_can_enable_feature(backend: BaseBackend):
    feature_name = f'{TEST_FEATURE}_three'
    backend.add(feature_name)
    backend.enable(feature_name, Gate.Boolean)
    f = backend.get(feature_name)
    assert f.state == 'on'


def test_can_enable_then_disable_feature(backend: BaseBackend):
    feature_name = f'{TEST_FEATURE}_four'
    backend.add(feature_name)
    backend.enable(feature_name, Gate.Boolean)
    f = backend.get(feature_name)
    assert f.state == 'on'
    backend.disable(feature_name, Gate.Boolean)
    f = backend.get(feature_name)
    assert f.state == 'off'


def test_can_enumerate_features(backend: BaseBackend):
    backend.add(f'{TEST_FEATURE}_first')
    backend.add(f'{TEST_FEATURE}_second')
    backend.add(f'{TEST_FEATURE}_third')
    features = backend.features()
    assert f'{TEST_FEATURE}_first' in features
    assert f'{TEST_FEATURE}_second' in features
    assert f'{TEST_FEATURE}_third' in features
