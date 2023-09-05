from dataclasses import dataclass
from flippy.backends.base import BaseBackend
from flippy.core import FeatureName, Gate
from flippy.exceptions import FeatureNotFound

ACTOR_IF_NO_TARGET = "anonymous"


@dataclass
class FeatureState:
    key: str
    boolean: bool | None
    actors: list[str]
    groups: list[str]
    percent_actors: int | None
    percent_time: int | None


class Flippy:
    """
    The `Flippy` object is the key interface to everything in Flippy.

    You can get ahold of one by passing in a backend, like this:
    
    ```python
    from flippy.backends import MemoryBackend
    from flippy import Flippy

    f = Flippy(MemoryBackend())
    ```
    """
    def __init__(self, backend: BaseBackend):
        """
        Available backends include:
        - `flippy.backends.MemoryBackend`
        - `flippy.backends.DjangoBackend`
        - `flippy.backends.FlipperCloudBackend`
        """
        self._backend = backend
    
    def is_enabled(self, feature: FeatureName, target = None) -> bool:
        """
        Checks whether a particular feature is enabled for a particular object
        (or globally, if you don't pass in a target).

        ```python
        # globally enabled?
        flippy.is_enabled('my_cool_feature')

        # enabled for this Django user?
        # (actually this will work for any object with a `pk` or `id` property)
        user = User.objects.get(pk=1)
        flippy.is_enabled('my_cool_feature', user)
        ```

        Targets are munged into "classname;id" so that they can round-trip through
        backends like Flipper Cloud just as well as they round-trip the Django ORM.
        This means that if you change the class name, objects will no longer be
        recognized if they were previously entered into Flippy. You can implement
        a `get_flipper_id` method on your object to precisely control this munging.
        We strongly suggest you use a similar scheme which "namespaces" IDs like
        the default implementation.

        ```python
        # enabled for an object with a get_flipper_id() method?
        @dataclass
        class Fruit:
            name: str
            produce_lookup_code: str

            # without this method, the default would be "Fruit;<id>", which you
            # may not want if you intend to also use produce lookup codes for,
            # say, vegetables. Instead we'll inject our own "PLU;" namespace.
            def get_flipper_id(self):
                return f"PLU;{self.produce_lookup_code}"
        
        banana = Fruit(name='banana', produce_lookup_code='4011')
        flippy.is_enabled('my_cool_feature', banana)
        ```
        """
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

        if any([
            f.actors_gate.is_open(actor, feature),
            f.groups_gate.is_open(actor, feature),
            f.percentage_of_actors_gate.is_open(actor, feature),
            f.percentage_of_time_gate.is_open(actor, feature),
            f.expression_gate.is_open(actor, feature),
        ]):
            return True
        
        # TODO: special check whether actor is a member of an enabled group
        # (using the Django authentication system)
        ...
        
        return False
    
    def create(self, feature: FeatureName) -> bool:
        """
        Create a new feature flag.

        You should always do this, either using the Flippy frontend or
        through some backend-specific mechanism. If you try to set a feature
        flag's state without explicitly creating it, it's up to the backend
        whether to support that or raise an exception.
        """
        return self._backend.add(feature)
    
    def get_all_feature_names(self) -> set[FeatureName]:
        """
        Get a list of all known feature flag names.
        """
        return {f.key for f in self._backend.get_all()}
    
    def feature_exists(self, feature: FeatureName) -> bool:
        """
        Check if a specific feature name is known to this backend.
        """
        try:
            self._backend.get(feature)
            return True
        except FeatureNotFound:
            return False
    
    def get_feature_state(self, feature: FeatureName) -> FeatureState:
        """
        Get a lot of detail about exactly how a feature flag is enabled.

        This is not recomended as a general practice for checking feature
        flag state. Instead, use `Flippy.is_enabled` for those uses.
        This method is provided so that it's possible to build a frontend
        (web, CLI, etc.) for controlling feature flags.
        """
        f = self._backend.get(feature)
        return FeatureState(
            key=f.key,
            boolean=f.boolean_gate.value,
            actors=f.actors_gate.value,
            groups=f.groups_gate.value,
            percent_actors=f.percentage_of_actors_gate.value,
            percent_time=f.percentage_of_time_gate.value,
        )
    
    def enable(self, feature: FeatureName) -> None:
        """
        Globally enable a particular feature flag. This means it's on for
        everyone, all the time, no matter what other states are set.
        """
        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.Boolean)
        except FeatureNotFound:
            pass

    def enable_actor(self, feature: FeatureName, target) -> None:
        """
        Enable a feature for a particular actor. Usually this would be a user,
        but there may be special situations where you want to use other kinds
        of actors.
        """
        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.Actors, self._to_flipper_id(target))
        except FeatureNotFound:
            pass
    
    def enable_group(self, feature: FeatureName, target) -> None:
        """
        Enable a feature for an entire group of actors.
        
        At the present moment, this is not plumbed into the Django notion of
        groups, so this method is little different _in practice_ from
        `Flippy.enable_actor`. (You have to explicitly get a reference to the
        actual group object and pass it as the `target` to `Flippy.is_enabled`.)
        The design goal and future intention, though, is that calling
        `Flippy.is_enabled` on a user who belongs to that group will return
        True if that user is a member of an enabled group.
        """
        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.Groups, self._to_flipper_id(target))
        except FeatureNotFound:
            pass
    
    def enable_percentage_of_actors(self, feature: FeatureName, percentage: int) -> None:
        """
        Enable a feature for a percentage of all actors.

        Backends are expected to use a stable mechanism to opt a particular
        actor into a particular feature flag at any percentage threshold. That is,
        if an actor is enabled at % = 10, then that same user must still be enabled
        at % = 11, 12, 13, ..., 100. Likewise, if an actor is _not_ enabled at
        % = 20, then that same actor must not be enabled at % = 19, 18, ..., 0.
        """
        assert isinstance(percentage, int)
        assert 0 <= percentage <= 100

        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.PercentageOfActors, percentage)
        except FeatureNotFound:
            pass

    def enable_percentage_of_time(self, feature: FeatureName, percentage: int) -> None:
        """
        Enable a feature for a percentage of all lookups.

        On average, a feature marked for "50% of time" should come up as
        "enabled" about as often as it comes up "disabled". This isn't great
        for features which modify user experience (since subsequent page loads
        might give the opposite result) but could be useful for safely rolling
        out things like performance optimizations.
        """
        assert isinstance(percentage, int)
        assert 0 <= percentage <= 100

        try:
            f = self._backend.get(feature)
            self._backend.enable(f.key, Gate.PercentageOfTime, percentage)
        except FeatureNotFound:
            pass

    def disable(self, feature: FeatureName) -> None:
        """
        Turn off global enablement of a particular feature flag. This means it's
        on for only those targets specifically opted into it (actors, groups, % of
        actors, % of time).

        If you intend to totally disable the feature for _everyone_, instead of
        this method, you want `Flippy.clear`.
        """
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.Boolean)
        except FeatureNotFound:
            pass

    def disable_actor(self, feature: FeatureName, target) -> None:
        """
        Remove an actor from the list of those enabled for the feature.
        """
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.Actors, self._to_flipper_id(target))
        except FeatureNotFound:
            pass
    
    def disable_group(self, feature: FeatureName, target) -> None:
        """
        Remove a group from the list of those enabled for the feature.
        """
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.Groups, self._to_flipper_id(target))
        except FeatureNotFound:
            pass
    
    def disable_percentage_of_actors(self, feature: FeatureName) -> None:
        """
        Disable the percentage-of-actors gate for a feature. This is the same
        as setting it to 0.
        """
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.PercentageOfActors)
        except FeatureNotFound:
            pass

    def disable_percentage_of_time(self, feature: FeatureName) -> None:
        """
        Disable the percentage-of-time gate for a feature. This is the same
        as setting it to 0.
        """
        try:
            f = self._backend.get(feature)
            self._backend.disable(f.key, Gate.PercentageOfTime)
        except FeatureNotFound:
            pass
    
    def clear(self, feature: FeatureName) -> bool:
        """
        Globally disable a particular feature flag. This is a destructive action
        which clears all state associated with the flag, setting it back to
        disabled for _everyone_ including those you had previously opted in.
        """
        return self._backend.clear(feature)

    def destroy(self, feature: FeatureName) -> bool:
        """
        Tell the backend to completely delete this feature flag. This is a
        destructive action clearing all state and removing the flag from the
        set of "known features".
        """
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
