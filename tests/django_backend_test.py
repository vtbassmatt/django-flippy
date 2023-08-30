import pytest

pytestmark = pytest.mark.django_db

from flippy.backends import DjangoBackend
from flippy.core import BaseBackend
from tests.backend_shared import *


@pytest.fixture
def backend() -> BaseBackend:
    return DjangoBackend()
