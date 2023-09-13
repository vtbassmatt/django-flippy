from abc import ABCMeta, abstractmethod
import json

from flippy.core import FeatureEncoder, FeatureName, Feature, Gate


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
    
    @abstractmethod
    def to_json(self) -> str:
        "Produce a JSON-formatted string containing state for all features."
        # default implementation; feel free to use or override
        features = {f.key: f for f in self.get_all()}
        return json.dumps(features, cls=FeatureEncoder, separators=(',', ':'))

    @abstractmethod
    def from_json(self, new_state: str) -> None:
        "Clear current state and replace with state from a JSON-formatted string."
        pass

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
