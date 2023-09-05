from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import lazy

from flippy import Flippy
from flippy.config import flippy_backend


class FeatureContext:
    def __init__(self, flippy: Flippy, name, request):
        self.flippy = flippy
        self.name = name
        self.request = request
    
    def for_user(self) -> bool:
        try:
            user = self.request.user
        except AttributeError:
            raise ImproperlyConfigured(
                "request.user doesn't exist; make sure "
                "django.contrib.auth.context_processors.auth is on in your settings."
            )
        return self.flippy.is_enabled(self.name, user)
    
    def globally(self) -> bool:
        return self.flippy.is_enabled(self.name)
    
    def __bool__(self):
        raise NotImplementedError(
            f"Asking for `flippy.{self.name}` isn't implemented. "
            "(It seems like a trap / easy typo to make, with unintended consequences.) "
            f"You probably want `flippy.{self.name}.globally` instead."
        )


class FlippyContext:
    def __init__(self, request):
        self.flippy = Flippy(flippy_backend)
        self.request = request
    
    def __getattr__(self, name: str) -> FeatureContext:
        if self.flippy.feature_exists(name):
            return FeatureContext(self.flippy, name, self.request)
        raise AttributeError(name=name, obj=self)


def processor(request):
    # Only instantiate the FlippyContext if someone actually requests it.
    # Because you have to call `flippy.<feature_name>`, the FeatureContext
    # is essentially already lazy.
    c = lambda: FlippyContext(request)
    return {
        'flippy': lazy(c, FlippyContext),
    }
