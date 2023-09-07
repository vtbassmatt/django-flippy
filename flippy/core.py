from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Literal, NewType

from flippy.gates import (ActorsGate, BooleanGate, ExpressionGate, GroupsGate,
                          PercentageOfActorsGate, PercentageOfTimeGate)

FeatureName = NewType('FeatureName', str)
"The (string) name of a feature."

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

    def __eq__(self, other):
        if not isinstance(other, Feature):
            return False
        
        return all([
            self.key == other.key,
            self.boolean_gate == other.boolean_gate,
            self.actors_gate == other.actors_gate,
            self.groups_gate == other.groups_gate,
            self.percentage_of_actors_gate == other.percentage_of_actors_gate,
            self.percentage_of_time_gate == other.percentage_of_time_gate,
            self.expression_gate == other.expression_gate,
        ])


class FeatureEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Feature):
            return obj.to_api()
        return json.JSONEncoder.default(self, obj)
