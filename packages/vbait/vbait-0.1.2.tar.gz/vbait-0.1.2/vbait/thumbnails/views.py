from django.http import Http404, HttpResponseBadRequest
from generator import Generator, BadRequest


def generate_image(request, path):
    if not path:
        raise Http404("Unable to find image file.")
    params = request.GET.copy().dict()
    try:
        generator = Generator(path, **params)
        generator.generate()
    except BadRequest as e:
        return HttpResponseBadRequest(e)
    return generator.response