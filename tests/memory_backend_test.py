import pytest

from flippy.backends import MemoryBackend
from flippy.core import BaseBackend, Gate


@pytest.fixture
def backend() -> BaseBackend:
    return MemoryBackend()


def test_add_feature(backend: BaseBackend):
    assert backend.add('foo_feature') == True


def test_feature_defaults_off(backend: BaseBackend):
    backend.add('foo_feature')
    f = backend.get('foo_feature')
    assert f.state == 'off'


def test_can_enable_feature(backend: BaseBackend):
    backend.add('foo_feature')
    backend.enable('foo_feature', Gate.Boolean)
    f = backend.get('foo_feature')
    assert f.state == 'on'


def test_can_enable_then_disable_feature(backend: BaseBackend):
    backend.add('foo_feature')
    backend.enable('foo_feature', Gate.Boolean)
    f = backend.get('foo_feature')
    assert f.state == 'on'
    backend.disable('foo_feature', Gate.Boolean)
    assert f.state == 'off'


def test_can_enumerate_features(backend: BaseBackend):
    backend.add('first_feature')
    backend.add('second_feature')
    backend.add('third_feature')
    features = backend.features()
    assert len(features) == 3
    assert 'first_feature' in features
    assert 'second_feature' in features
    assert 'third_feature' in features
