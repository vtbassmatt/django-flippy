from flippy.core import BaseBackend, FeatureName, Gate
from flippy.exceptions import FeatureNotFound

ACTOR_IF_NO_TARGET = "anonymous"

class Flippy:
    def __init__(self, backend: BaseBackend):
        self._backend = backend
    
    def is_enabled(self, feature: FeatureName, target = None) -> bool:
        try:
            f = self._backend.get(feature)
        except FeatureNotFound:
            return False

        # if the boolean gate is on or off, that's final
        match f.state:
            case 'on':
                return True
            case 'off':
                return False

        # if the feature is conditional and no target was given, use a constant
        if target is None:
            actor = ACTOR_IF_NO_TARGET
        else:
            actor = self._to_flipper_id(target)

        return any([
            f.actors_gate.is_open(actor, feature),
            f.groups_gate.is_open(actor, feature),
            f.percentage_of_actors_gate.is_open(actor, feature),
            f.percentage_of_time_gate.is_open(actor, feature),
            f.expression_gate.is_open(actor, feature),
        ])
    
    def create(self, feature: FeatureName) -> bool:
        return self._backend.add(feature)
    
    def get_all_feature_names(self) -> set[FeatureName]:
        return {f.key for f in self._backend.get_all()}
    
    def feature_exists(self, feature: FeatureName) -> bool:
        try:
            self._backend.get(feature)
            return True
        except FeatureNotFound:
            return False
    
    def enable(self, feature: FeatureName) -> None:
        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.Boolean)
        except FeatureNotFound:
            pass

    def enable_actor(self, feature: FeatureName, target) -> None:
        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.Actors, self._to_flipper_id(target))
        except FeatureNotFound:
            pass
    
    def enable_group(self, feature: FeatureName, target) -> None:
        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.Groups, self._to_flipper_id(target))
        except FeatureNotFound:
            pass
    
    def enable_percentage_of_actors(self, feature: FeatureName, percentage: int) -> None:
        assert isinstance(percentage, int)
        assert 0 <= percentage <= 100

        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.PercentageOfActors, percentage)
        except FeatureNotFound:
            pass

    def enable_percentage_of_time(self, feature: FeatureName, percentage: int) -> None:
        assert isinstance(percentage, int)
        assert 0 <= percentage <= 100

        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.PercentageOfTime, percentage)
        except FeatureNotFound:
            pass

    def disable(self, feature: FeatureName) -> None:
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.Boolean)
        except FeatureNotFound:
            pass

    def disable_actor(self, feature: FeatureName, target) -> None:
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.Actors, self._to_flipper_id(target))
        except FeatureNotFound:
            pass
    
    def disable_group(self, feature: FeatureName, target) -> None:
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.Groups, self._to_flipper_id(target))
        except FeatureNotFound:
            pass
    
    def disable_percentage_of_actors(self, feature: FeatureName) -> None:
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.PercentageOfActors)
        except FeatureNotFound:
            pass

    def disable_percentage_of_time(self, feature: FeatureName) -> None:
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.PercentageOfTime)
        except FeatureNotFound:
            pass
    
    def clear(self, feature: FeatureName) -> bool:
        return self._backend.clear(feature)

    def destroy(self, feature: FeatureName) -> bool:
        return self._backend.remove(feature)

    def _to_flipper_id(self, object) -> str:
        if hasattr(object, 'get_flipper_id'):
            return object.get_flipper_id()

        type_name = object.__class__.__name__
        object_id = None

        if hasattr(object, 'flipper_id'):
            object_id = object.flipper_id
        elif hasattr(object, 'pk'):
            object_id = object.pk
        elif hasattr(object, 'id'):
            object_id = object.id
        else:
            # TODO: check if this is stable over time
            object_id = hash(object)
        
        return f"{type_name};{object_id}"
