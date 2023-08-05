# coding=utf-8
from functools import wraps

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import authenticate

from errors.services import Unauthorized


def token_auth(view_func):
    @wraps(view_func)
    def _wrapped_view_func(cls_obj, request, *args, **kwargs):
        if not request.user.is_authenticated():
            token = request.META.get('HTTP_TOKEN', None)
            if token:
                request.user = authenticate(token=token) or AnonymousUser()

        if request.user and request.user.is_authenticated():
            response = view_func(cls_obj, request, *args, **kwargs)
        else:
            raise Unauthorized
        return response
    return _wrapped_view_func


def basic_auth(view_func):
    @wraps(view_func)
    def _wrapped_view_func(cls_obj, request, *args, **kwargs):
        if not request.user.is_authenticated():
            auth_string = request.META.get('HTTP_AUTHORIZATION', None)
            if auth_string:
                (authmeth, auth) = auth_string.split(" ", 1)
                if authmeth.lower() == 'basic':
                    try:
                        auth = auth.strip().decode('base64')
                        (username, password) = auth.split(':', 1)
                        request.user = authenticate(username=username, password=password) or AnonymousUser()
                    except Exception:
                        pass

        if request.user and request.user.is_authenticated():
            response = view_func(cls_obj, request, *args, **kwargs)
        else:
            raise Unauthorized
        return response
    return _wrapped_view_func