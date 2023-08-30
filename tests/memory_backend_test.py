import pytest

from flippy.backends import MemoryBackend
from flippy.core import BaseBackend
from tests.backend_shared import *


@pytest.fixture
def backend() -> BaseBackend:
    return MemoryBackend()
