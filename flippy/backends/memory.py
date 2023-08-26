from flippy.core import BaseFlippy, Feature, FeatureName
from flippy.exceptions import FeatureNotFound
from flippy.gates import (ActorsGate, BooleanGate, ExpressionGate, Gate,
                          GroupsGate, PercentageOfActorsGate,
                          PercentageOfTimeGate)


class MemoryFlippy(BaseFlippy):
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
            return self._features[feature]
        except KeyError:
            raise FeatureNotFound(feature)

    def enable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Enable a gate for a thing."
        feature = self._features[feature]

        match gate:
            case BooleanGate():
                feature.boolean_gate.value = True
                return True
            case ActorsGate():
                if thing and thing not in feature.actors_gate.value:
                    feature.actors_gate.value.append(thing)
                    return True
                return False
            case GroupsGate():
                if thing and thing not in feature.groups_gate.value:
                    feature.groups_gate.value.append(thing)
                    return True
                return False
            case PercentageOfActorsGate():
                # TODO: check if thing is int
                feature.percentageofactors_gate.value = thing
                return True
            case PercentageOfTimeGate():
                # TODO: check if thing is int
                feature.percentageoftime_gate.value = thing
                return True
            case ExpressionGate():
                raise NotImplementedError("ExpressionGate isn't supported")
            case _:
                raise ValueError(f"{gate} is not a known gate type")

    def disable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Disable a gate for a thing."
        feature = self._features[feature]

        match gate:
            case BooleanGate():
                feature.boolean_gate.value = False
                return True
            case ActorsGate():
                if thing and thing in feature.actors_gate.value:
                    feature.actors_gate.value.remove(thing)
                    return True
                return False
            case GroupsGate():
                if thing and thing in feature.groups_gate.value:
                    feature.groups_gate.value.remove(thing)
                    return True
                return False
            case PercentageOfActorsGate():
                feature.percentageofactors_gate.value = None
                return True
            case PercentageOfTimeGate():
                feature.percentageoftime_gate.value = None
                return True
            case ExpressionGate():
                raise NotImplementedError("ExpressionGate isn't supported")
            case _:
                raise ValueError(f"{gate} is not a known gate type")

    def get_multi(self, features: list[FeatureName]) -> list[Feature]:
        "Get all gate values for several features at once."
        return super().get_multi(features)

    def get_all(self) -> list[Feature]:
        "Get all gate values for all features at once."
        return super().get_all()
