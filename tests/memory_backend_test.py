import pytest

from flippy.backends import BaseBackend, MemoryBackend
from tests.backend_shared import *


@pytest.fixture
def backend() -> BaseBackend:
    return MemoryBackend()
