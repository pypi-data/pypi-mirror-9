from django.db.models.query import QuerySet
import os
from django.db.models.fields.files import ImageFieldFile
from django.utils import six
from django.db import models


class ResourceOptions(object):
    method_allowed = ()

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


class BaseService(six.with_metaclass(DeclarativeMetaclass)):
    def __init__(self, user=None):
        self.user = user

    def unpack_model_objects(self, obj):
        if isinstance(obj, (list, set, QuerySet)):
            items = []
            for ii in obj:
                items.append(self.unpack_model_object(ii))
            return items
        else:
            return self.unpack_model_object(obj)

    def unpack_model_object(self, obj):
        if isinstance(obj, models.Model):
            item = self.model_to_dict(obj)
            return item
        return None

    def model_to_dict(self, instance, fields=None, exclude=None):
        from django.db.models.fields.related import ManyToManyField
        opts = instance._meta
        data = {}
        for f in opts.concrete_fields + opts.virtual_fields + opts.many_to_many:
            #if not getattr(f, 'editable', False):
            #    continue
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if isinstance(f, ManyToManyField):
                continue
            else:
                value = f.value_from_object(instance)
                if isinstance(value, ImageFieldFile):
                    value = {
                        'url': value.url,
                        'size': value.size,
                        'name': value.name,
                        'filename': os.path.basename(value.name)
                    } if value.name else None
                data[f.name] = value
        return data

    def objects_to_paging(self, objects, page=1, per_page=20):
        count = 0
        page_objects = []
        if isinstance(objects, QuerySet):
            count = objects.count()
        elif isinstance(objects, list):
            count = objects.__len__()
        if count > 0:
            page_objects = objects[(page-1)*per_page: page*per_page]
        return {
            "count": count,
            "page": page,
            "per_page": per_page,
            "data": page_objects
        }