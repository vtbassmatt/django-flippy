from flippy import Flippy
from flippy.backends import DjangoBackend


def flippy_middleware(get_response):
    flippy = Flippy(DjangoBackend())

    def middleware(request):
        request.flippy = flippy
        response = get_response(request)
        return response
    return middleware
