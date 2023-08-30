from django.shortcuts import render

from flippy import Flippy
from flippy.backends import DjangoBackend

FLIPPY = Flippy(DjangoBackend())


def index(request):
    feature_exists = FLIPPY.feature_exists('background_red')

    return render(
        request,
        'index.html',
        {
            'feature_exists': feature_exists,
        }
    )


# GET requests for mutating state aren't great. But, this GET request
# is idempotent (plus it's a demo), so it's kind of OK.
def setup(request):
    if not FLIPPY.feature_exists('background_red'):
        FLIPPY.create('background_red')

    return render(
        request,
        'setup_complete.html',
        {}
    )
