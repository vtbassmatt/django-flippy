import json

from flippy.backends import BaseBackend
from flippy.core import Feature, FeatureEncoder, FeatureName, Gate
from flippy.exceptions import FeatureNotFound

from django.core.exceptions import ImproperlyConfigured
try:
    from flippy.models import FlippyFeature, FlippyActorGate, FlippyGroupGate
except ImproperlyConfigured:
    pass

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


class DjangoBackend(BaseBackend):
    """
    A backend implemented as Django models.
    """
    def features(self) -> set[FeatureName]:
        "Get the set of known features."
        return set([f.key for f in FlippyFeature.objects.all()])

    def add(self, feature: FeatureName) -> bool:
        "Add a feature to the set of known features."
        try:
            FlippyFeature(key=feature).save()
            return True
        except IntegrityError:
            return False

    def remove(self, feature: FeatureName) -> bool:
        "Remove a feature from the set of known features."
        try:
            feature = FlippyFeature.objects.get(key=feature)
            feature.delete()
            return True
        except FlippyFeature.DoesNotExist:
            return False

    def clear(self, feature: FeatureName) -> bool:
        "Clear all gate values for a feature."
        try:
            feature = FlippyFeature.objects.get(key=feature)
            feature.clear()
            return True
        except FlippyFeature.DoesNotExist:
            return False

    def get(self, feature: FeatureName) -> Feature:
        "Get all gate values for a feature."
        try:
            feature = FlippyFeature.objects.get(key=feature)
            return feature.as_feature()
        except FlippyFeature.DoesNotExist:
            raise FeatureNotFound(feature)

    def enable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Enable a gate for a thing."
        try:
            feature = FlippyFeature.objects.get(key=feature)
        except FlippyFeature.DoesNotExist:
            return False

        match gate:
            case Gate.Boolean:
                feature.boolean = True
                feature.save()
                return True
            case Gate.Actors:
                try:
                    feature.enabled_actors.create(key=thing)
                    return True
                except IntegrityError:
                    return False
            case Gate.Groups:
                try:
                    feature.enabled_groups.create(key=thing)
                    return True
                except IntegrityError:
                    return False
            case Gate.PercentageOfActors:
                try:
                    feature.percentage_of_actors = thing
                    feature.save()
                    return True
                except ValidationError:
                    return False
            case Gate.PercentageOfTime:
                try:
                    feature.percentage_of_time = thing
                    feature.save()
                    return True
                except ValidationError:
                    return False
            case Gate.Expression:
                raise NotImplementedError("ExpressionGate isn't supported")
            case _:
                raise ValueError(f"{gate} is not a known gate type")

    def disable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Disable a gate for a thing."
        try:
            feature = FlippyFeature.objects.get(key=feature)
        except FlippyFeature.DoesNotExist:
            return False

        match gate:
            case Gate.Boolean:
                feature.boolean = False
                feature.save()
                return True
            case Gate.Actors:
                try:
                    feature.enabled_actors.get(key=thing).delete()
                    return True
                except FlippyActorGate.DoesNotExist:
                    return False
            case Gate.Groups:
                try:
                    feature.enabled_groups.get(key=thing).delete()
                    return True
                except FlippyGroupGate.DoesNotExist:
                    return False
            case Gate.PercentageOfActors:
                try:
                    feature.percentage_of_actors = None
                    feature.save()
                    return True
                except ValidationError:
                    return False
            case Gate.PercentageOfTime:
                try:
                    feature.percentage_of_time = None
                    feature.save()
                    return True
                except ValidationError:
                    return False
            case Gate.Expression:
                raise NotImplementedError("ExpressionGate isn't supported")
            case _:
                raise ValueError(f"{gate} is not a known gate type")

    def get_multi(self, features: list[FeatureName]) -> list[Feature]:
        "Get all gate values for several features at once."
        features = FlippyFeature.objects.filter(key__in=features)
        return [f.as_feature() for f in features]

    def get_all(self) -> list[Feature]:
        "Get all gate values for all features at once."
        features = FlippyFeature.objects.all()
        return [f.as_feature() for f in features]

    def to_json(self) -> str:
        "Produce a JSON-formatted string containing state for all features."
        return super().to_json()

    def from_json(self, new_state: str) -> None:
        "Clear current state and replace with state from a JSON-formatted string."
        return self._from_json_naive(new_state)

    def _from_json_naive(self, new_state: str) -> None:
        FlippyFeature.objects.all().delete()
        features_raw = json.loads(new_state)
        for value in features_raw.values():
            f = Feature.from_api(value)
            # FlippyFeature.from_feature saves the object
            ff = FlippyFeature.from_feature(f)
