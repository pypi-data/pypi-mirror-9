from copy import copy
from functools import wraps
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import json
from django.http import HttpResponseNotFound, Http404, HttpResponse
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import six
from django.utils.functional import Promise
from django.views.decorators.csrf import csrf_exempt

from errors.services import NotFound, Unauthorized, ValidationError, PermissionDenied, MethodNotImplemented
from errors import http


logger = logging.getLogger('error_server')


def method_allowed(*methods):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view_func(cls_obj, request, *args, **kwargs):
            if request.method.lower() in methods:
                response = view_func(cls_obj, request, *args, **kwargs)
                return response
            allows = ', '.join([meth.upper() for meth in methods])
            response = http.HttpMethodNotAllowed(allows)
            response['Allow'] = allows
            return response

        return _wrapped_view_func

    return decorator


def decode_data(params_mapping, data, exclude_params=None):
    new_data = dict()
    for key, value in params_mapping.items():
        if isinstance(value, dict):
            param_value = copy(value.get("params", {}))
            value = data.get(value.get("key", None), None)
            if value:
                new_data[key] = decode_data(param_value, value, exclude_params)
        else:
            if exclude_params is None:
                new_data[key] = data.get(value, None)
            elif data.has_key(value):
                new_data[key] = data.get(value, None)

    return new_data


def mapping(exclude_params=None, **params_mapping):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view_func(cls_obj, request, *args, **kwargs):
            data = request.data or {}
            request.data = decode_data(params_mapping, data, exclude_params)
            try:
                return view_func(cls_obj, request, *args, **kwargs)
            except ValidationError as e:
                if e.message.has_key('fields'):
                    e.message['fields'] = BaseWebApi().mapping_data(e.message['fields'], **params_mapping)
                raise e

        return _wrapped_view_func

    return decorator


def response_mapping(cls, mapping_path=None, auto_encode=False):
    """
    if data doesn't have 'mapping_path' then data will mapped all
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view_func(cls_obj, request, *args, **kwargs):
            data = view_func(cls_obj, request, *args, **kwargs)
            if mapping_path:
                try:
                    input_data = data.pop(mapping_path)
                    map_data = cls(mapping_path).encode({mapping_path: input_data}, auto_encode)
                    data = BaseWebApi().mapping_data(data)
                    data[mapping_path] = map_data
                    return data
                except TypeError:
                    return cls(None).encode(data, auto_encode)
            return cls(mapping_path).encode(data, auto_encode)
        return _wrapped_view_func

    return decorator


class JsonEncoder(json.DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return unicode(o)
        elif isinstance(o, set):
            return list(o)
        return super(JsonEncoder, self).default(o)


class ResourceOptions(object):
    default_format = "application/json"
    method_suffix = {
        'get': '',
        'detail': '_detail',
        'post': '_add',
        'put': '_update',
        'delete': '_delete',
        'patch': '_patch'
    }

    def __new__(cls, meta=None):
        overrides = {}
        if meta:
            for override_name in dir(meta):
                if not override_name.startswith('_'):
                    overrides[override_name] = getattr(meta, override_name)

        if six.PY3:
            return object.__new__(type('ResourceOptions', (cls,), overrides))
        else:
            return object.__new__(type(b'ResourceOptions', (cls,), overrides))


class DeclarativeMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(DeclarativeMetaclass, cls).__new__(cls, name, bases, attrs)
        opts = getattr(new_class, 'Meta', None)
        new_class._meta = ResourceOptions(opts)
        return new_class


class BaseWebApi(six.with_metaclass(DeclarativeMetaclass)):
    def method(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            obj_id = kwargs.get('obj_id', None)
            try:
                method = request.method.lower()
                if method == "get" and obj_id:
                    method = "detail"
                convert_view = "%s%s" % (view, self._meta.method_suffix[method])
                self.convert_request_data(request)
                if hasattr(self, convert_view):
                    callback = getattr(self, convert_view)
                else:
                    callback = getattr(self, view)
                response = callback(request, *args, **kwargs)
                if settings.DEBUG and request.GET.has_key('debug'):
                    template = get_template("test.html")
                    html = template.render(RequestContext(request, {"data": response}))
                    return HttpResponse(html)
                return self.response(response)
            except Unauthorized as e:
                return self.error_response(request, e.message, response_class=http.HttpUnauthorized)
            except PermissionDenied as e:
                return self.error_response(request, e.message, response_class=http.HttpForbidden)
            except NotFound as e:
                return self.error_response(request, e.message, response_class=http.HttpNotFound)
            except ValidationError as e:
                return self.error_response(request, e.message, response_class=http.HttpBadRequest)
            except MethodNotImplemented as e:
                return self.error_response(request, e.message, response_class=http.HttpNotImplemented)
            except Exception as e:
                if hasattr(e, 'response'):
                    return e.response
                return self._handle_500(request, e)

        return wrapper

    def convert_request_data(self, request):
        request.data = None
        request.files = None

        if request.method.lower() in ['put', 'patch']:
            def_method = str(request.method.upper())
            if hasattr(request, '_post'):
                del (request._post)
                del (request._files)
            request.method = "POST"
            request._load_post_and_files()
            request.method = def_method
            setattr(request, def_method, request.POST)

        if request.method.lower() in ['post', 'put', 'patch']:
            if request.FILES:
                request.files = request.FILES.copy()

            content_type = request.META['CONTENT_TYPE'].split(';')[0].lower()
            if content_type == "application/json":
                try:
                    request.data = json.json.loads(request.body) if request.body else None
                except ValueError:
                    raise ValidationError("No json serialize")
            elif content_type == "text/plain":
                request.data = request.body if request.body else None
            elif content_type == "application/x-www-form-urlencoded":
                request.data = request.POST.copy()
            elif content_type == "multipart/form-data":
                request.data = request.POST.copy()
                if request.files:
                    request.data.update(request.files)
        elif request.GET:
            request.data = request.GET.copy()

    def error_response(self, request, errors, response_class=None):
        if response_class is None:
            response_class = http.HttpBadRequest

        try:
            return self.json_response(errors, response_class)
        except Exception as e:
            error = "Additional errors occurred, but serialization of those errors failed."
            if settings.DEBUG:
                error += " %s" % e
            return response_class(content=error, content_type='text/plain')

    def _handle_500(self, request, exception):
        import traceback
        import sys

        the_trace = '\n'.join(traceback.format_exception(*(sys.exc_info())))
        response_class = http.HttpApplicationError
        response_code = 500

        logger.error('Internal Server Error: %s' % request.path, exc_info=True,
                     extra={'status_code': response_code, 'request': request})

        NOT_FOUND_EXCEPTIONS = (NotFound, ObjectDoesNotExist, Http404)

        if isinstance(exception, NOT_FOUND_EXCEPTIONS):
            response_class = HttpResponseNotFound

        if settings.DEBUG:
            data = {
                "error_message": six.text_type(exception),
                "traceback": the_trace,
            }
            return self.error_response(request, data, response_class=response_class)

        data = {
            "error_message": "Sorry, this request could not be processed. Please try again later."
        }
        return self.error_response(request, data, response_class=response_class)

    def mapping_data(self, data, **kwargs):
        if isinstance(data, dict):
            return self.mapping_item(data, **kwargs)
        elif isinstance(data, list):
            return self.mapping_list(data, **kwargs)
        return data

    def mapping_list(self, data, **kwargs):
        new_data = []
        for item in data:
            if isinstance(item, dict):
                new_data.append(self.mapping_item(item, **kwargs))
            elif isinstance(item, list):
                new_data.append(self.mapping_list(item, **kwargs))
            else:
                new_data.append(item)
        return new_data

    def mapping_item(self, data, **kwargs):
        new_item = dict()
        for key, value in data.items():
            if kwargs and kwargs.has_key(key):
                new_key = kwargs[key]
            else:
                key_components = [component.title() for component in key.split('_')]
                new_key = key_components[0].lower() + "".join(key_components[1:]) \
                    if key_components.__len__() > 1 else key_components[0].lower()
            if isinstance(new_key, dict):
                new_key = new_key.get('key', 'undefined')
            if isinstance(value, dict):
                new_item[new_key] = self.mapping_item(value, **kwargs)
            elif isinstance(value, list):
                new_item[new_key] = self.mapping_list(value, **kwargs)
            else:
                new_item[new_key] = value
        return new_item

    def response(self, data):
        if self._meta.default_format == "application/json":
            return self.json_response(data)
        elif self._meta.default_format == "text/xml":
            return self.xml_response(data)
        else:
            return data

    def json_response(self, data, response_class=None):
        if isinstance(data, HttpResponse):
            return data
        if not response_class:
            response_class = HttpResponse
        data_convert = json.json.dumps(data, cls=JsonEncoder, sort_keys=True, ensure_ascii=False)
        return response_class(data_convert, content_type=self._meta.default_format)

    def xml_response(self, data, response_class=None):
        if isinstance(data, HttpResponse):
            return data
        if not response_class:
            response_class = HttpResponse
        return response_class(data, content_type="%s;charset=utf-8" % self._meta.default_format)