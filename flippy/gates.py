from dataclasses import dataclass
from typing import Any, Literal, NewType

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

Gate = (
    BooleanGate | ActorsGate | GroupsGate | 
    PercentageOfActorsGate | PercentageOfTimeGate |
    ExpressionGate
)
