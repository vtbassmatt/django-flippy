from flippy import Flippy
from flippy.config import flippy_backend


def flippy_middleware(get_response):
    flippy = Flippy(flippy_backend)

    def middleware(request):
        request.flippy = flippy
        response = get_response(request)
        return response
    return middleware
