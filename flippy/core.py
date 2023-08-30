from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, NewType

from flippy.gates import (ActorsGate, BooleanGate, ExpressionGate, GroupsGate,
                          PercentageOfActorsGate, PercentageOfTimeGate)

FeatureName = NewType('FeatureName', str)

FlagState = Literal['on', 'conditional', 'off']


class Gate(Enum):
    Boolean = 'boolean'
    Actors = 'actors'
    Groups = 'groups'
    PercentageOfActors = 'percentage_of_actors'
    PercentageOfTime = 'percentage_of_time'
    Expression = 'expression'


@dataclass
class Feature:
    key: FeatureName

    @property
    def state(self) -> FlagState:
        if self.boolean_gate.value:
            return 'on'
        if (self.actors_gate.value == []
            and self.groups_gate.value == []
            and self.percentage_of_actors_gate.value == None
            and self.percentage_of_time_gate.value == None
            and self.expression_gate.value == None):
            return 'off'
        return 'conditional'

    boolean_gate: BooleanGate = field(default_factory=BooleanGate)
    actors_gate: ActorsGate = field(default_factory=ActorsGate)
    groups_gate: GroupsGate = field(default_factory=GroupsGate)
    percentage_of_actors_gate: PercentageOfActorsGate = field(default_factory=PercentageOfActorsGate)
    percentage_of_time_gate: PercentageOfTimeGate = field(default_factory=PercentageOfTimeGate)
    expression_gate: ExpressionGate = field(default_factory=ExpressionGate)

    def to_api(self):
        return {
            'key': self.key,
            'state': self.state,
            'gates': [
                self.boolean_gate.to_api(),
                self.actors_gate.to_api(),
                self.groups_gate.to_api(),
                self.percentage_of_actors_gate.to_api(),
                self.percentage_of_time_gate.to_api(),
                self.expression_gate.to_api(),
            ]
        }
    
    @classmethod
    def from_api(cls, api_payload: dict):
        self = cls(api_payload['key'])
        for gate in api_payload['gates']:
            gateValue = gate['value']
            match gate['key']:
                case 'boolean':
                    self.boolean_gate.value = gateValue
                case 'actors':
                    self.actors_gate.value = gateValue
                case 'groups':
                    self.groups_gate.value = gateValue
                case 'percentage_of_actors':
                    self.percentage_of_actors_gate.value = None if gateValue is None else int(gateValue)
                case 'percentage_of_time':
                    self.percentage_of_time_gate.value = None if gateValue is None else int(gateValue)
                case 'expression':
                    self.expression_gate.value = gateValue
                case _:
                    raise ValueError(f"{gate} is not a known gate type")
        return self


class BaseBackend(metaclass=ABCMeta):
    """
    Flipper established a protocol for adapters to implement.
    This is the Pythonic implementation of it.
    
    https://www.flippercloud.io/docs/adapters/new
    """
    @abstractmethod
    def features(self) -> set[FeatureName]:
        "Get the set of known features."
        pass

    @abstractmethod
    def add(self, feature: FeatureName) -> bool:
        "Add a feature to the set of known features."
        pass

    @abstractmethod
    def remove(self, feature: FeatureName) -> bool:
        "Remove a feature from the set of known features."
        pass

    @abstractmethod
    def clear(self, feature: FeatureName) -> bool:
        "Clear all gate values for a feature."
        pass

    @abstractmethod
    def get(self, feature: FeatureName) -> Feature:
        "Get all gate values for a feature."
        pass

    @abstractmethod
    def enable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Enable a gate for a thing."
        pass

    @abstractmethod
    def disable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Disable a gate for a thing."
        pass

    @abstractmethod
    def get_multi(self, features: list[FeatureName]) -> list[Feature]:
        "Get all gate values for several features at once."
        # default implementation; feel free to use or override
        values = []
        for feature in features:
            values.append(self.get(feature))
        return values

    @abstractmethod
    def get_all(self) -> list[Feature]:
        "Get all gate values for all features at once."
        # default implementation; feel free to use or override
        values = []
        for feature in self.features():
            values.append(self.get(feature))
        return values

    # dict implementation
    # note, there's no setting of values because that doesn't fit the
    # dict contract cleanly
    def __len__(self):
        return len(self.features())
    
    def __getitem__(self, key: FeatureName):
        return self.get(key)
    
    def __delitem__(self, key: FeatureName):
        return self.remove(key)
    
    def __iter__(self):
        return iter(self.features())
    
    def __contains__(self, key: FeatureName):
        return key in self.features()
    # end dict implementation

BaseBackend.register(dict)
