from os.path import join, abspath, dirname
import json
from django.conf import settings


class GenerateErrorsCodes():
    class __GenerateErrorsCodes:
        def __init__(self):
            here = lambda *x: join(abspath(dirname(__file__)), *x)
            filepath = getattr(settings, "VBPLATFORM_ERROR_CODE_FILEPATH", join(here(), "errors_code.json"))
            self.list = json.load(open(filepath))

        def __str__(self):
            return repr(self)

        def get_code(self, code):
            for error in self.list:
                if error["code"] == code:
                    return error
            return None

    instance = None

    def __init__(self):
        if not GenerateErrorsCodes.instance:
            GenerateErrorsCodes.instance = GenerateErrorsCodes.__GenerateErrorsCodes()

    def __getattr__(self, name):
        return getattr(self.instance, name)

errors_codes = GenerateErrorsCodes()


class VBError(Exception):
    def __init__(self, message=None, code=None):
        self.message = dict()
        if message and isinstance(message, (str, unicode,)):
            self.message = {'message': message}
        elif isinstance(message, dict):
            self.message = message
        else:
            self.message = {'message': unicode(message) if message else ''}
        if code:
            self.message.update({"error": errors_codes.get_code(code)})


class ValidationError(VBError):
    """
    response 400
    """
    pass


class Unauthorized(VBError):
    """
    response 401
    """
    pass


class PermissionDenied(VBError):
    """
    response 403
    """
    pass


class NotFound(VBError):
    """
    response 404
    """
    pass


class MethodNotImplemented(VBError):
    """
    response 501
    """