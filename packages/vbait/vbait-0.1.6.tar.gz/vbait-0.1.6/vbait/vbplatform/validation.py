# coding=utf-8
from decimal import Decimal
from functools import wraps
import datetime
from django.utils.dateparse import parse_datetime, parse_date

from django.core import exceptions, validators
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import phonenumbers

from errors.services import ValidationError


def decode_to_type(value, types):
    if value is None:
        return None
    new_value = None
    for t in types:
        if t == datetime.datetime:
            new_value = decode_to_datetime(value)
            continue
        elif t == datetime.date:
            new_value = decode_to_date(value)
            continue
        new_value = t(value) if new_value is None else t(new_value)
    return new_value


def decode_to_datetime(value):
    try:
        parsed = parse_datetime(value)
        if parsed is not None:
            return parsed
    except ValueError:
        pass
    raise ValidationError(_(u"Не валидные входные данные"))


def decode_to_date(value):
    try:
        parsed = parse_date(value)
        if parsed is not None:
            return parsed
    except ValueError:
        pass
    raise ValidationError(_(u"Не валидные входные данные"))


def validate_fields(data, options):
    if data is None:
        data = dict()
    errors = dict()
    for name, params in options.items():
        validator = ValidParam(name)
        validator.create_validators(data, **params)
        try:
            valid_value = validator.run_validators(data.get(name))
            if not valid_value is None:
                data[name] = valid_value
        except ValidationError as e:
            e.message['limit_value'] = params.get(e.message['code'])
            if params.has_key('messages'):
                e.message['message'] = unicode(params['messages'].get(e.message['code'], e.message['message']))
            errors[name] = e.message
    if errors:
        raise ValidationError({
            'message': unicode(_(u"Не валидные входные данные")),
            'fields': errors
        }, 1)
    return data


def validate_input(options):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view_func(cls_obj, data=None, *args, **kwargs):
            data = validate_fields(data, options)
            return view_func(cls_obj, data, *args, **kwargs)
        return _wrapped_view_func
    return decorator


def validate_filter(options):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view_func(cls_obj, data, *args, **kwargs):
            data = data or {}
            filter = data.get('filter')
            validate_filter_params = dict()
            if filter:
                for name, params in options.items():
                    values = filter.get(name)
                    if not values:
                        continue
                    is_array = params.get('is_array', False)
                    type_val = params.get('type', 'str')

                    if is_array and isinstance(values, (str, unicode)):
                        values = [values]
                    elif not is_array and isinstance(values, list):
                        values = values[0]

                    decode_types = [unicode]
                    if type_val == 'integer':
                        decode_types = [int]
                    elif type_val == 'bool':
                        decode_types = [int, bool]
                    elif type_val == 'datetime':
                        decode_types = [datetime.datetime]
                    elif type_val == 'date':
                        decode_types = [datetime.date]
                    try:
                        values = [decode_to_type(val, decode_types) for val in values] \
                            if isinstance(values, list) else decode_to_type(values, decode_types)
                    except ValueError:
                        continue
                    except ValidationError as e:
                        raise ValidationError({
                            'message': unicode(_(u"Не валидные входные данные")),
                            'fields': {str(name): {"message": e.message}}
                        }, 1)
                    validate_filter_params[str(name)] = values
            data['filter'] = validate_filter_params
            return view_func(cls_obj, data, *args, **kwargs)
        return _wrapped_view_func
    return decorator


def validate_order(*fields, **base_kwargs):
    """
    format = 0 - with asc and desc
    format = 1 - with '-' or empty
    format = 2 - django order_by format
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view_func(cls_obj, data=None, *args, **kwargs):
            format_item = base_kwargs.get('format', 0)
            data = data or {}
            default_order_items = map(lambda x: x.keys()[0], base_kwargs.get("default") or [])
            order_items = data.get('order') or base_kwargs.get("default") or []
            if not isinstance(order_items, list):
                order_items = []
            items = []
            all_fields = list(fields) + default_order_items
            for item in order_items or []:
                field = item.keys()[0]
                if not field in all_fields:
                    continue
                if format_item == 1:
                    items.append({field: "-" if item[field] == "desc" else ""})
                elif format_item == 2:
                    items.append(("-" if item[field] == "desc" else "") + field)
                else:
                    items.append(item)
            data['order'] = items
            return view_func(cls_obj, data, *args, **kwargs)
        return _wrapped_view_func
    return decorator


class ValidParam(object):
    def __init__(self, name):
        self.validators = []
        self.name = name

    def create_validators(self, data, **kwargs):
        if kwargs.has_key("default"):
            self.validators.append(DefaultValidator(kwargs.get("default")))
        if kwargs.get("required") or kwargs.get("required") is None:
            self.validators.append(RequiredValidator(None))
        elif not data.get(self.name):
            return

        if kwargs.get("min_length"):
            self.validators.append(validators.MinLengthValidator(kwargs.get("min_length")))
        if kwargs.get("max_length"):
            self.validators.append(validators.MaxLengthValidator(kwargs.get("max_length")))
        if kwargs.get("type"):
            self.validators.append(ConvertToTypeValidator(kwargs.get("type")))
        if kwargs.has_key("min_value"):
            self.validators.append(validators.MinValueValidator(kwargs.get("min_value")))
        if kwargs.has_key("max_value"):
            self.validators.append(validators.MaxValueValidator(kwargs.get("max_value")))
        if kwargs.get("equal_to"):
            self.validators.append(EqualToValidator(data.get(kwargs["equal_to"])))

        if kwargs.get("validation_type") and kwargs.get("validation_type") == "email":
            self.validators.append(validators.EmailValidator())
        elif kwargs.get("validation_type") and kwargs.get("validation_type") == "phone":
            self.validators.append(PhoneNumberValidator(kwargs.get("format")))
        elif kwargs.get("validation_type") and kwargs.get("validation_type") == "datetime":
            self.validators.append(DateTimeValidator())
        elif kwargs.get("validation_type") and kwargs.get("validation_type") == "file":
            self.validators.append(FileValidator())

    def add_custom_validators(self, vs):
        if vs:
            self.validators = self.validators + vs

    def run_validators(self, value):
        new_value = None
        for v in self.validators:
            try:
                res = v(new_value if not new_value is None else value)
                if not res is None:
                    new_value = res
            except exceptions.ValidationError as e:
                error = {'message': unicode(e.messages[0]), 'code': None}
                if hasattr(e, 'code'):
                    error['code'] = e.code
                raise ValidationError(error)
        return new_value


class RequiredValidator(validators.BaseValidator):
    #clean = lambda self, x: None if isinstance(x, (str, unicode)) and x.__len__() == 0 else x
    compare = lambda self, a, b: a is b
    message = _('This field cannot be null.')
    code = 'required'

    def clean(self, x):
        if isinstance(x, (str, unicode)) and x.__len__() == 0:
            return None
        elif isinstance(x, list) and x.__len__() == 0:
            return None
        else:
            return x

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {'limit_value': self.limit_value, 'show_value': cleaned}
        if self.compare(cleaned, self.limit_value):
            raise exceptions.ValidationError(self.message, code=self.code, params=params)


class DefaultValidator(validators.BaseValidator):
    message = _('Error.')
    code = 'default'

    def __call__(self, value):
        cleaned = self.clean(value)
        return cleaned or self.limit_value


class EqualToValidator(validators.BaseValidator):
    compare = lambda self, a, b: a != b
    message = _("The two fields didn't match.")
    code = 'equal_to'

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {'limit_value': self.limit_value, 'show_value': cleaned}
        if self.compare(cleaned, self.limit_value):
            raise exceptions.ValidationError(self.message, code=self.code, params=params)


class PhoneNumberValidator(validators.BaseValidator):
    clean = lambda self, x: force_text(x)
    message = _('Enter a valid phone number.')
    code = 'invalid'
    formats = {
        "INTERNATIONAL": phonenumbers.PhoneNumberFormat.E164,
        "NATIONAL": phonenumbers.PhoneNumberFormat.NATIONAL
    }
    messages = {
        0: _(u"INVALID_COUNTRY_CODE"),
        1: _(u"NOT_A_NUMBER"),
        2: _(u"TOO_SHORT_AFTER_IDD"),
        3: _(u"TOO_SHORT_NSN"),
        4: _(u"TOO_LONG")
    }

    def __init__(self, format="INTERNATIONAL"):
        super(PhoneNumberValidator, self).__init__(limit_value=None)
        self.format = format
        if not self.format in self.formats.keys():
            self.format = "INTERNATIONAL"

    def __call__(self, value):
        cleaned = self.clean(value)
        try:
            phone = phonenumbers.parse(cleaned, None)
        except phonenumbers.NumberParseException as e:
            raise exceptions.ValidationError(self.messages.get(e.error_type, self.message),
                                             code=self.code, params={'show_value': cleaned})
        is_valid = phonenumbers.is_valid_number(phone)
        if not is_valid:
            raise exceptions.ValidationError(self.message, code=self.code, params={'show_value': cleaned})
        return phonenumbers.format_number(phone, self.formats[self.format])\
            .replace(' ', '').replace('+', '').replace('-', '')


class DateTimeValidator(validators.BaseValidator):
    clean = lambda self, x: force_text(x)
    message = _('Enter a valid date.')
    code = 'invalid'
    ISO_8601 = 'iso-8601'
    input_formats = list(settings.DATETIME_INPUT_FORMATS)  # formats.get_format_lazy('DATETIME_INPUT_FORMATS')
    input_formats += [ISO_8601]

    def __init__(self):
        super(DateTimeValidator, self).__init__(limit_value=None)

    def __call__(self, value):
        cleaned = self.clean(value)
        parsed = None

        for format in self.input_formats:
            if format.lower() == self.ISO_8601:
                try:
                    parsed = parse_datetime(cleaned)
                except (ValueError, TypeError):
                    continue
            else:
                try:
                    parsed = datetime.datetime.strptime(cleaned, format)
                except (ValueError, TypeError):
                    continue
        if not parsed:
            raise exceptions.ValidationError(self.message, code=self.code, params={'show_value': cleaned})
        return parsed


class FileValidator(validators.BaseValidator):
    def __init__(self):
        super(FileValidator, self).__init__(limit_value=None)

    def __call__(self, value):
        pass


class ConvertToTypeValidator(validators.BaseValidator):
    compare = lambda self, x: x
    message = _("Value not type %s")
    code = 'type'

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {'limit_value': self.limit_value, 'show_value': cleaned}
        try:
            if self.limit_value == "text":
                cleaned = unicode(cleaned)
            elif self.limit_value == "decimal":
                cleaned = Decimal(cleaned)
            elif self.limit_value == "integer":
                cleaned = int(cleaned)
            elif self.limit_value == "bool":
                cleaned = bool(int(cleaned))
            return cleaned
        except ValueError:
            raise exceptions.ValidationError(self.message % self.limit_value, code=self.code, params=params)