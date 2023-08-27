from dataclasses import dataclass
from typing import Any, Literal, NewType, TYPE_CHECKING
import random
from zlib import crc32

if TYPE_CHECKING:
    from flippy.core import FeatureName

Percentage = NewType('Percentage', int)


@dataclass
class BooleanGate:
    key: Literal['boolean']
    name: Literal['boolean']
    value: bool | None

    def __init__(self, value: bool | None=None):
        self.key = self.name = 'boolean'
        self.value = value

    def to_api(self):
        return {
            'key': self.key,
            'name': self.name,
            'value': self.value,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        return bool(self.value)

@dataclass
class ActorsGate:
    key: Literal['actors']
    name: Literal['actor']
    value: list[str]

    def __init__(self, value: list[str]=None):
        self.key = 'actors'
        self.name = 'actor'
        self.value = value or []

    def to_api(self):
        return {
            'key': self.key,
            'name': self.name,
            'value': self.value,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        return target in self.value

@dataclass
class GroupsGate:
    key: Literal['groups']
    name: Literal['group']
    value: list[str]

    def __init__(self, value: list[str]=None):
        self.key = 'groups'
        self.name = 'group'
        self.value = value or []

    def to_api(self):
        return {
            'key': self.key,
            'name': self.name,
            'value': self.value,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        return target in self.value

@dataclass
class PercentageOfActorsGate:
    key: Literal['percentage_of_actors']
    name: Literal['percentage_of_actors']
    value: Percentage | None

    def __init__(self, value: Percentage | None=None):
        self.key = self.name = 'percentage_of_actors'
        self.value = value

    def to_api(self):
        return {
            'key': self.key,
            'name': self.name,
            'value': str(self.value) if self.value is not None else None,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        if self.value is None:
            return False
        if self.value == 100:
            return True

        # Roughly we need to:
        # - stably mash the target + feature name into a number 0-100
        # - compare that result to self.value
        # - return (our number < self.value)
        # The reason for strict less-than is so that if self.value is set to
        # 0, no actors slip through.
        feature_hash = crc32(feature.encode())
        target_hash = crc32(target.encode(), feature_hash)
        target_value = round(100 * target_hash / 2**32)
        return target_value < self.value

@dataclass
class PercentageOfTimeGate:
    key: Literal['percentage_of_time']
    name: Literal['percentage_of_time']
    value: Percentage | None

    def __init__(self, value: Percentage | None=None):
        self.key = self.name = 'percentage_of_time'
        self.value = value

    def to_api(self):
        return {
            'key': self.key,
            'name': self.name,
            'value': str(self.value) if self.value is not None else None,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        if self.value is None:
            return False

        r = random.randint(0, 100)
        return self.value >= r

@dataclass
class ExpressionGate:
    key: Literal['expression']
    name: Literal['expression']
    value: Any # TODO

    def __init__(self, value=None):
        self.key = self.name = 'expression'
        self.value = value

    def to_api(self):
        return {
            'key': self.key,
            'name': self.name,
            'value': self.value,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        return False

Gate = (
    BooleanGate | ActorsGate | GroupsGate | 
    PercentageOfActorsGate | PercentageOfTimeGate |
    ExpressionGate
)
