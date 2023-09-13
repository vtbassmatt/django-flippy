import copy
import json

from flippy.backends import BaseBackend
from flippy.core import Feature, FeatureEncoder, FeatureName, Gate
from flippy.exceptions import FeatureNotFound


class MemoryBackend(BaseBackend):
    """A memory-only implementation of Flippy."""
    def __init__(self):
        self._features: dict[FeatureName: Feature] = {}

    def features(self) -> set[FeatureName]:
        "Get the set of known features."
        return self._features.keys()

    def add(self, feature: FeatureName) -> bool:
        "Add a feature to the set of known features."
        if feature in self._features:
            return False
        self._features[feature] = Feature(key=feature)
        return True

    def add_feature(self, feature: Feature) -> bool:
        "Add a fully hydrated feature, such as from an API call."
        if feature.key in self._features:
            return False
        self._features[feature.key] = feature
        return True

    def remove(self, feature: FeatureName) -> bool:
        "Remove a feature from the set of known features."
        try:
            self._features.pop(feature)
            return True
        except KeyError:
            return False

    def clear(self, feature: FeatureName) -> bool:
        "Clear all gate values for a feature."
        if feature not in self._features:
            return False
        self._features[feature] = Feature(key=feature)

    def get(self, feature: FeatureName) -> Feature:
        "Get all gate values for a feature."
        try:
            return copy.deepcopy(self._features[feature])
        except KeyError:
            raise FeatureNotFound(feature)

    def enable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Enable a gate for a thing."
        feature = self._features[feature]

        match gate:
            case Gate.Boolean:
                feature.boolean_gate.value = True
                return True
            case Gate.Actors:
                if thing and thing not in feature.actors_gate.value:
                    feature.actors_gate.value.append(thing)
                    return True
                return False
            case Gate.Groups:
                if thing and thing not in feature.groups_gate.value:
                    feature.groups_gate.value.append(thing)
                    return True
                return False
            case Gate.PercentageOfActors:
                # TODO: check if thing is int
                feature.percentage_of_actors_gate.value = thing
                return True
            case Gate.PercentageOfTime:
                # TODO: check if thing is int
                feature.percentage_of_time_gate.value = thing
                return True
            case Gate.Expression:
                raise NotImplementedError("ExpressionGate isn't supported")
            case _:
                raise ValueError(f"{gate} is not a known gate type")

    def disable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Disable a gate for a thing."
        feature = self._features[feature]

        match gate:
            case Gate.Boolean:
                feature.boolean_gate.value = False
                return True
            case Gate.Actors:
                if thing and thing in feature.actors_gate.value:
                    feature.actors_gate.value.remove(thing)
                    return True
                return False
            case Gate.Groups:
                if thing and thing in feature.groups_gate.value:
                    feature.groups_gate.value.remove(thing)
                    return True
                return False
            case Gate.PercentageOfActors:
                feature.percentageofactors_gate.value = None
                return True
            case Gate.PercentageOfTime:
                feature.percentageoftime_gate.value = None
                return True
            case Gate.Expression:
                raise NotImplementedError("ExpressionGate isn't supported")
            case _:
                raise ValueError(f"{gate} is not a known gate type")

    def get_multi(self, features: list[FeatureName]) -> list[Feature]:
        "Get all gate values for several features at once."
        return super().get_multi(features)

    def get_all(self) -> list[Feature]:
        "Get all gate values for all features at once."
        return super().get_all()

    def to_json(self) -> str:
        "Produce a JSON-formatted string containing state for all features."
        return json.dumps(self._features, cls=FeatureEncoder, separators=(',', ':'))

    def from_json(self, new_state: str) -> None:
        "Clear current state and replace with state from a JSON-formatted string."
        self._features = {}
        features_raw = json.loads(new_state)
        for k, v in features_raw.items():
            self._features[k] = Feature.from_api(v)
