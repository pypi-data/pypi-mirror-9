import datetime
from PIL import ImageDraw
from django.core.files.storage import default_storage
from django.http import HttpResponse, Http404
from PIL import Image
import os, time, cStringIO as StringIO


class BadRequest(Exception):
    pass


class Generator(object):
    formats = {
        'png': 'png',
        'jpg': 'jpeg',
        'gif': 'jpeg',
        'jpeg': 'jpeg'
    }

    def __init__(self, path, **kwargs):
        self.path = path
        self.fmt = kwargs.pop('fmt', os.path.splitext(self.path)[1][1:])
        self.fmt = self.fmt.lower()
        self.content_type = 'image/png'
        if not self.fmt in self.formats.keys():
            self.fmt = "jpeg"
            self.content_type = 'image/jpeg'

        try:
            self.wid = int(kwargs.pop('wid', 0))
            self.hei = int(kwargs.pop('hei', 0))
            self.qlt = int(kwargs.pop('qlt', 80))
            self.cache = int(kwargs.pop('cache', 0))
            self.fill = int(kwargs.pop('fill', 0))
        except ValueError:
            raise BadRequest("Bad params.")
        if self.qlt > 100:
            self.qlt = 100

        self._file = None
        self.storage = kwargs.pop('storage', default_storage)

    def _generate_path_for_cache(self):
        name, extension = os.path.splitext(self.path)
        name = "%s_%d_%d_%d" % (name, self.wid, self.hei, self.qlt)
        if self.fill:
            name += "_fill"
        return "%s.%s" % (name, self.fmt)

    def generate(self, is_verify_by_date=True):
        path = self._generate_path_for_cache()
        if not self.cache:
            if self.storage.exists(path):
                if not is_verify_by_date:
                    self._file = self.storage.open(path)
                    return
                cr_date_thumb = datetime.datetime.fromtimestamp((os.path.getctime(self.storage.path(path))))
                try:
                    md_date_base = datetime.datetime.fromtimestamp(os.path.getmtime(self.storage.path(self.path)))
                except OSError:
                    raise Http404("Unable to find image file.")
                if md_date_base < cr_date_thumb:
                    self._file = self.storage.open(path)
                    return

        stream = StringIO.StringIO()
        if not self.cache:
            stream = self.storage.path(path)

        try:
            im = Image.open(self.storage.path(self.path))
            if self.fmt == 'gif':
                im = im.convert('RGB')
            def_size = im.size
            size = (self.wid or def_size[0], self.hei or def_size[1])
            im.thumbnail(size, Image.ANTIALIAS)
            #print im.size
            if self.fill:
                img = Image.new("RGBA" if self.fmt == "png" else "RGB", size, 0 if self.fmt == "png" else "white")
                img.paste(im, ((size[0] - im.size[0])/2, (size[1] - im.size[1])/2))
                im = img
            im.save(stream, self.formats[self.fmt], quality=self.qlt)
            self._file = stream
            try:
                self._file.seek(0)
            except AttributeError:
                self._file = self.storage.open(path)
        except KeyError:
            raise BadRequest("No suppot extension")
        except IOError:
            raise Http404("Unable to find image file.")

    @property
    def response(self):
        return HttpResponse(self._file.read(), content_type=self.content_type)