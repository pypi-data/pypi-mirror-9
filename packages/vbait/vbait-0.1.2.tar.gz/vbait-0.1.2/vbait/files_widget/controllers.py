# coding=utf-8
from django.core.urlresolvers import reverse
import re
import urllib
import os, os.path
from datetime import datetime

from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.functional import curry
from django.core.files.images import ImageFile
from django.contrib.staticfiles import finders
from conf import *


class FilePath(unicode):
    def __new__(cls, str, instance=None, field=None):
        value = unicode(str or '')
        try:
            path_to_file, name, is_prime = value.split('||')
            is_prime = True
        except ValueError:
            path_to_file, name = value.split('||') if value else [None, None]
            is_prime = False

        self = super(FilePath, cls).__new__(cls, str.strip())
        #self.path_to_file = path_to_file
        self.path = path_to_file
        self.name = name
        self.is_prime = is_prime

        self._instance = instance
        self._field = field
        self._exists = None
        self._size = None
        self._accessed_time = None
        self._created_time = None
        self._modified_time = None
        return self

    def _html_attrs(self, **kwargs):
        attrs = {}
        attrs.update(kwargs)
        if 'css_class' in attrs:
            attrs['class'] = attrs['css_class']
            del attrs['css_class']
        return attrs

    def upload_to(self):
        return self._field.upload_to

    @property
    def unescaped(self):
        return urllib.unquote(self.path_to_file)

    @property
    def escaped(self):
        return urllib.quote(self.unescaped)

    @property
    def url(self):
        if not self.path_to_file.startswith('/') and self.path_to_file.find('//') == -1:
            return os.path.join(MEDIA_URL, self.escaped)
        return self.escaped

    @property
    def local_path(self):
        if not self.path_to_file.startswith('/') and self.path_to_file.find('//') == -1:
            return os.path.join(MEDIA_ROOT, urllib.unquote(self.path_to_file))
        return self

    def _get_local_path_or_file(self):
        # if file is in static instead of media directory, sorl raises
        # a suspicious operation error. So we open it safely without errors.

        if self.startswith('/'):
            if self.startswith('/static/'):
                path = self.replace('/static/', '')
            elif self.startswith(settings.STATIC_URL):
                path = self.replace(settings.STATIC_URL, '')
            else:
                return self.local_path
        else:
            return self.local_path

        path = finders.find(urllib.unquote(path))
        image = ImageFile(open(path, 'r'))
        return image

    @property
    def filename(self):
        return urllib.unquote(re.sub(r'^.+\/', '', self.path_to_file))

    @property
    def display_name(self):
        without_extension = re.sub(r'\.[\w\d]+$', '', self.filename)
        with_spaces = re.sub(r'_', ' ', without_extension)
        return with_spaces

    @property
    def ext(self):
        return re.sub(r'^.+\.', '', self.filename)

    def exists(self):
        if self._exists == None:
            self._exists = os.path.exists(self.local_path)
        return self._exists

    def get_size(self):
        if self._size == None:
            self._size = os.path.getsize(self.local_path)
        return self._size

    def get_accessed_time(self):
        if self._accessed_time == None:
            self._accessed_time = datetime.fromtimestamp(os.path.getatime(self.local_path))
        return self._accessed_time

    def get_created_time(self):
        if self._created_time == None:
            self._created_time = datetime.fromtimestamp(os.path.getctime(self.local_path))
        return self._created_time

    def get_modified_time(self):
        if self._modified_time == None:
            self._modified_time = datetime.fromtimestamp(os.path.getmtime(self.local_path))
        return self._modified_time

    def prime(self):
        return self.is_prime


class ImagePath(FilePath):
    def __new__(cls, str, instance=None, field=None):
        self = super(ImagePath, cls).__new__(cls, str, instance, field)
        return self

    def __getattr__(self, attr):
        thumbnail_mxn = re.match(r'^thumbnail_(tag_)?(\d*x?\d+)$', attr)
        if thumbnail_mxn:
            tag = thumbnail_mxn.group(1) == 'tag_'
            size = thumbnail_mxn.group(2)
            if tag:
                return curry(self.thumbnail_tag, size)
            else:
                return curry(self.thumbnail, size)

        raise AttributeError


class FilePaths(unicode):
    item_class = FilePath

    def __new__(cls, str, instance=None, field=None):
        self = super(FilePaths, cls).__new__(cls, str)
        self._instance = instance
        self._field = field
        self._all = None
        self._prime = None
        self._length = None
        self._current = 0
        return self

    def upload_to(self):
        return self._field.upload_to

    def all(self):
        if self._all == None:
            self._all = []
            prime = None
            for f in self.splitlines():
                item = self._field.attr_class.item_class(f, self._instance, self._field)
                if item.is_prime:
                    prime = item
                else:
                    self._all.append(item)
            if prime:
                self._all = [prime] + self._all
            self._length = len(self._all)
        return self._all

    @property
    def default_image(self):
        if self.prime():
            return self.prime()
        if self.all():
            return self.all()[0]
        return None

    def prime(self):
        for img in self.all():
            if img.is_prime:
                self._prime = img
                break
        return self._prime

    def count(self):
        self.all()
        return self._length

    def first(self):
        return self.all() and self.all()[0] or None

    def last(self):
        return self.all() and self.all()[-1] or None

    def next(self):
        f = self.all()[self._current]
        self._current += 1
        return f

    def next_n(self, n):
        files = self.all()[self._current:self._current+n]
        self._current += n
        return files

    def next_all(self):
        files = self.all()[self._current:]
        self._current = self._length - 1
        return files

    def has_next(self):
        self.all()
        return max(0, self._length - self._current - 1)

    def reset(self):
        self._current = 0

    def __getattr__(self, attr):
        next_n = re.match(r'^next_(\d+)$', attr)
        if next_n:
            n = int(next_n.group(1))
            return curry(self.next_n, n)

        raise AttributeError


class ImagePaths(FilePaths):
    item_class = ImagePath

    def as_gallery(self):
        raise NotImplementedError

    def as_carousel(self):
        raise NotImplementedError


class FilesDescriptor(object):
    """
    Used django.db.models.fields.files.FileDescriptor as an example.
    This descriptor returns an unicode object, with special methods
    for formatting like filename(), absolute(), relative() and img_tag().
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))

        files = instance.__dict__[self.field.name]
        if isinstance(files, six.string_types) and not isinstance(files, (FilePath, FilePaths)):
            attr = self.field.attr_class(files, instance, self.field)
            instance.__dict__[self.field.name] = attr

        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value
