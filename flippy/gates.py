import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NewType
from zlib import crc32

if TYPE_CHECKING:
    from flippy.core import FeatureName

Percentage = NewType('Percentage', int)


@dataclass
class BooleanGate:
    value: bool | None = None

    def to_api(self):
        return {
            'key': 'boolean',
            'name': 'boolean',
            'value': self.value,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        return bool(self.value)

    def __eq__(self, other):
        if not isinstance(other, BooleanGate):
            return False
        
        return self.value == other.value

@dataclass
class ActorsGate:
    value: list[str]

    def __init__(self, value: list[str]=None):
        self.value = value or []

    def to_api(self):
        return {
            'key': 'actors',
            'name': 'actor',
            'value': self.value,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        return target in self.value

    def __eq__(self, other):
        if not isinstance(other, ActorsGate):
            return False

        if self.value is None or other.value is None:
            return False
        
        return sorted(self.value) == sorted(other.value)

@dataclass
class GroupsGate:
    value: list[str]

    def __init__(self, value: list[str]=None):
        self.value = value or []

    def to_api(self):
        return {
            'key': 'groups',
            'name': 'group',
            'value': self.value,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        return target in self.value

    def __eq__(self, other):
        if not isinstance(other, GroupsGate):
            return False
        
        if self.value is None or other.value is None:
            return False
        
        return sorted(self.value) == sorted(other.value)

@dataclass
class PercentageOfActorsGate:
    value: Percentage | None = None

    def to_api(self):
        return {
            'key': 'percentage_of_actors',
            'name': 'percentage_of_actors',
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

    def __eq__(self, other):
        if not isinstance(other, PercentageOfActorsGate):
            return False
        
        return self.value == other.value

@dataclass
class PercentageOfTimeGate:
    value: Percentage | None = None

    def to_api(self):
        return {
            'key': 'percentage_of_time',
            'name': 'percentage_of_time',
            'value': str(self.value) if self.value is not None else None,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        if self.value is None:
            return False

        r = random.randint(0, 100)
        return self.value >= r

    def __eq__(self, other):
        if not isinstance(other, PercentageOfTimeGate):
            return False
        
        return self.value == other.value

@dataclass
class ExpressionGate:
    value: Any = None # TODO

    def to_api(self):
        return {
            'key': 'expression',
            'name': 'expression',
            'value': self.value,
        }

    def is_open(self, target: str, feature: 'FeatureName'):
        return False

    def __eq__(self, other):
        if not isinstance(other, ExpressionGate):
            return False

        return self.value == other.value
