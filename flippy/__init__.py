import importlib.metadata
from flippy.flippy import Flippy

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except:
    __version__ = "0.0.1-dev"


__all__ = [
    Flippy,
]
