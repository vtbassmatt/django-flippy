from dataclasses import dataclass
from http import HTTPStatus

from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseNotFound)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

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


USER = User(name='Jane Doe', id=1)
GROUP = Group(name='Power Users', id=15)


def index(request):
    feature_exists = request.flippy.feature_exists('background_red')
    feature_state = request.flippy.get_feature_state('background_red') if feature_exists else None

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
                request.flippy.clear('background_red')
            case 'bool-on':
                request.flippy.enable('background_red')
            case 'bool-off':
                request.flippy.disable('background_red')
            case 'add-user':                
                request.flippy.enable_actor('background_red', USER)
            case 'remove-user':
                request.flippy.disable_actor('background_red', USER)
            case 'add-group':
                request.flippy.enable_group('background_red', GROUP)
            case 'remove-group':
                request.flippy.disable_group('background_red', GROUP)
            case 'percent-less':
                actors = request.flippy.get_feature_state('background_red').percent_actors
                if actors:
                    request.flippy.enable_percentage_of_actors('background_red', actors - 10)
            case 'percent-more':
                actors = request.flippy.get_feature_state('background_red').percent_actors
                if not actors:
                    request.flippy.enable_percentage_of_actors('background_red', 10)
                elif actors < 100:
                    request.flippy.enable_percentage_of_actors('background_red', actors + 10)
            case 'time-less':
                time = request.flippy.get_feature_state('background_red').percent_time
                if time:
                    request.flippy.enable_percentage_of_time('background_red', time - 10)
            case 'time-more':
                time = request.flippy.get_feature_state('background_red').percent_time
                if not time:
                    request.flippy.enable_percentage_of_time('background_red', 10)
                elif time < 100:
                    request.flippy.enable_percentage_of_time('background_red', time + 10)
            case _:
                return HttpResponseNotFound()

        return HttpResponseCreated()
    else:
        raise HttpResponseNotAllowed(request.method)


# GET requests for mutating state aren't great. But, this GET request
# is idempotent (plus it's a demo), so it's kind of OK.
def setup(request):
    if not request.flippy.feature_exists('background_red'):
        request.flippy.create('background_red')

    return render(
        request,
        'setup_complete.html',
        {}
    )


def app(request):
    is_enabled = (
        request.flippy.is_enabled('background_red', USER)
        | request.flippy.is_enabled('background_red', GROUP)
    )
    return render(
        request,
        'app.html',
        {
            # ugly pattern, FIXME
            'flippy': {'background_red': is_enabled}
        }
    )
