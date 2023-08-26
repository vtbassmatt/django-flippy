import typing

if typing.TYPE_CHECKING:
    from flippy.core import FeatureName


class FeatureNotFound(Exception):
    def __init__(self, feature: 'FeatureName', parent_exception: Exception | None = None, *args: object) -> None:
        self.parent_exception = parent_exception
        super().__init__(feature, *args)


class GroupNotRegistered(Exception): pass
class PercentageInvalid(Exception): pass
class FlipperIdInvalid(Exception): pass
class NameInvalid(Exception): pass
