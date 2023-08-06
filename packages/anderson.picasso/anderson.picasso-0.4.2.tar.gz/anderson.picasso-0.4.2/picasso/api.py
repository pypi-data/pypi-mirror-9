# -*- coding:utf-8 -*-
from PIL import Image
from Queue import Queue, Empty
import os
from StringIO import StringIO
from threading import Thread
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


_picasso_queue = Queue()


class PicassoOpener(object):
    @classmethod
    def open(cls, image_path):
        """
        @param image_path(string) : the path of a image.
        """
        if image_path and isinstance(image_path, basestring) and os.path.exists(image_path):
            image = Image.open(image_path, 'r')
            try:
                image.verify()
            except:
                return None
            finally:
                image = Image.open(image_path, 'r')
        return image

    @classmethod
    def open_file(cls, imageFile):
        image = None
        try:
            output = StringIO(imageFile.read())
            image = Image.open(output, 'r')
            image.verify()
        except Exception as e:
            raise e
            return None
        finally:
            output.seek(0)
            image = Image.open(output, 'r')
        return image

    @classmethod
    def open_string(cls, data):
        if data and isinstance(data, basestring):
            try:
                image = Image.open(StringIO(data))
            except IOError:
                return None

        try:
            image.verify()
        except:
            return None
        return Image.open(StringIO(data))


class Picasso(object):
    def __init__(self):
        self._init()

    def _init(self):
        # Open
        self._image = None
        self._format = None

        # Resize
        self._resized = False
        self._reqWidth = -1
        self._reqHeight = -1
        self._centerCrop = False
        self._overSize = False

    def open(self, image):
        self._init()
        self._image = image
        return self

    def resize(self, width, height):
        """
        @param width(int): the pixel size of width
        @param height(int): the pixel size of height
        @param ratio(bool): keeps the ratio if true
        """
        self._resized = True
        self._reqWidth = width
        self._reqHeight = height
        return self

    def centerCrop(self, centerCrop):
        """
        @param centerCrop (bool)
        """
        self._centerCrop = bool(centerCrop)
        return self

    def overSize(self, overSize):
        """
        @param overSize : whether the request size can exceed the original size (w,h)
        """
        self._overSize = bool(overSize)

    def execute(self):
        self._open()
        if self._resized: self._resize()
        return self

    def _open(self):


        if isinstance(self._image, Image.Image):  # PIL
            pass
        elif isinstance(self._image, basestring) and os.path.exists(self._image):
            self._image = PicassoOpener.open(self._image)
        elif isinstance(self._image, basestring):
            self._image = PicassoOpener.open_string(self._image)
        elif isinstance(self._image, InMemoryUploadedFile):
            self._image = PicassoOpener.open_file(self._image)
        elif isinstance(self._image, TemporaryUploadedFile):
            self._image = PicassoOpener.open_file(self._image)
        elif isinstance(self._image, Picasso):
            self._image = self._image
        elif self._image and hasattr(self._image, 'read'):
            self._image = PicassoOpener.open_file(self._image)

        # Set Format
        if self._image and hasattr(self._image, 'format') and self._image.format:
            self._format = self._image.format

        if not self._image or not self._format:
            raise RuntimeError(str(self._image) + " " + str(type(self._image)) + " cannot be instantiated")

    def _resize(self):
        width, height = self._image.size

        reqWidth = self._reqWidth
        reqHeight = self._reqHeight
        if reqWidth < 0:
            reqWidth = width

        if self._reqHeight <= 0:
            reqHeight = int(self._reqWidth * height / width)

        if not self._overSize:
            if reqWidth >= width:
                reqWidth = width;
            if reqHeight >= height:
                reqHeight = height

        widthForReqHeight = int(round(width * reqHeight / height))  # x : reqHeight = width : height
        heightForReqWidth = int(round(reqWidth * height / width))  # reqWidth : y = width : height

        if widthForReqHeight >= reqWidth:
            pilImage = self._image.resize((widthForReqHeight, reqHeight), Image.ANTIALIAS)
            if self._centerCrop:
                pilImage = pilImage.crop((widthForReqHeight / 2 - reqWidth / 2, 0,
                                          widthForReqHeight / 2 + reqWidth / 2, reqHeight))

        else:
            pilImage = self._image.resize((reqWidth, heightForReqWidth), Image.ANTIALIAS)
            if self._centerCrop:
                pilImage = pilImage.crop((0, heightForReqWidth / 2 - reqHeight / 2,
                                          reqWidth, heightForReqWidth / 2 + reqHeight / 2))
        self._image = pilImage

    def save(self, path, format=None):
        if not format:
            format = self._format
        self._image.save(path, format=format)

    def to_stringIO(self):
        self._open()
        io = StringIO()
        self._image.save(io, self._image.format)
        io.seek(0)
        return io

    @property
    def size(self):
        return self._image.size

    @property
    def image(self):
        return self._image

    @property
    def format(self):
        self._open()
        return self._format


class PicassoThread(Thread):
    def __init__(self):
        super(PicassoThread, self).__init__()
        global _picasso_queue
        self._queue = _picasso_queue

    def run(self):
        while True:
            try:
                data = _picasso_queue.get(timeout=600)
            except Empty as e:
                print e
                break

            command = data.pop('command')
            picasso = data.pop('picasso')
            callback = data.pop('callback')
            args = data.pop('args') or []
            kwargs = data.pop('kwargs') or {}

            if command == 'process':
                picasso.execute()

            if callback:
                callback(picasso, *args, **kwargs)

            _picasso_queue.task_done()
            if _picasso_queue.empty():
                break


class PicassoManager(object):
    def __init__(self):
        global _picasso_queue
        self._queue = _picasso_queue
        self._t = None

    def put(self, picasso, callback=None, args=None, kwargs=None):
        data = {}
        data['command'] = 'process'
        data['picasso'] = picasso
        data['callback'] = callback
        data['args'] = args
        data['kwargs'] = kwargs
        self._queue.put(data)
        self._create_thread()

    def join(self):
        if self._t and self._t.is_alive():
            self._t.join()

    def _create_thread(self):
        if not self._t or not self._t.is_alive():
            del self._t
            self._t = PicassoThread()
            self._t.setDaemon(True)
            self._t.start()

def get_picasso_manager():
    if not hasattr(get_picasso_manager, '_instance') or not get_picasso_manager._instance:
        get_picasso_manager._instance = PicassoManager()
    return get_picasso_manager._instance






