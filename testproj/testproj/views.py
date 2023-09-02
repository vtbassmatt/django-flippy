from dataclasses import dataclass
from http import HTTPStatus

from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseNotFound)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from flippy import Flippy
from flippy.backends import DjangoBackend

# these could be Django models, but a dataclass will do for
# demonstration purposes
@dataclass
class User:
    name: str
    id: int

@dataclass
class Group:
    name: str
    id: int


FLIPPY = Flippy(DjangoBackend())
USER = User(name='Jane Doe', id=1)
GROUP = Group(name='Power Users', id=15)


def index(request):
    feature_exists = FLIPPY.feature_exists('background_red')
    feature_state = FLIPPY.get_feature_state('background_red') if feature_exists else None

    return render(
        request,
        'index.html',
        {
            'feature_exists': feature_exists,
            'feature_state': feature_state,
        }
    )


class HttpResponseCreated(HttpResponse):
    status_code = HTTPStatus.CREATED


# This is totally, completely, hilariously insecure. Please don't ever
# do something like this view in an internet-facing application.
@csrf_exempt
def control(request, command: str):
    if request.method == 'POST':
        match command:
            case 'clear':
                FLIPPY.clear('background_red')
            case 'bool-on':
                FLIPPY.enable('background_red')
            case 'bool-off':
                FLIPPY.disable('background_red')
            case 'add-user':                
                FLIPPY.enable_actor('background_red', USER)
            case 'remove-user':
                FLIPPY.disable_actor('background_red', USER)
            case 'add-group':
                FLIPPY.enable_group('background_red', GROUP)
            case 'remove-group':
                FLIPPY.disable_group('background_red', GROUP)
            case 'percent-less':
                actors = FLIPPY.get_feature_state('background_red').percent_actors
                if actors:
                    FLIPPY.enable_percentage_of_actors('background_red', actors - 10)
            case 'percent-more':
                actors = FLIPPY.get_feature_state('background_red').percent_actors
                if not actors:
                    FLIPPY.enable_percentage_of_actors('background_red', 10)
                elif actors < 100:
                    FLIPPY.enable_percentage_of_actors('background_red', actors + 10)
            case 'time-less':
                time = FLIPPY.get_feature_state('background_red').percent_time
                if time:
                    FLIPPY.enable_percentage_of_time('background_red', time - 10)
            case 'time-more':
                time = FLIPPY.get_feature_state('background_red').percent_time
                if not time:
                    FLIPPY.enable_percentage_of_time('background_red', 10)
                elif time < 100:
                    FLIPPY.enable_percentage_of_time('background_red', time + 10)
            case _:
                return HttpResponseNotFound()

        return HttpResponseCreated()
    else:
        raise HttpResponseNotAllowed(request.method)


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


def app(request):
    is_enabled = (
        FLIPPY.is_enabled('background_red', USER)
        | FLIPPY.is_enabled('background_red', GROUP)
    )
    return render(
        request,
        'app.html',
        {
            'flippy': {'background_red': is_enabled}
        }
    )
