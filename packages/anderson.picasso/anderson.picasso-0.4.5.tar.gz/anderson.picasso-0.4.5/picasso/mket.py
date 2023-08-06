# -*- coding:utf-8 -*-
from PIL import Image
from StringIO import StringIO
import os
import re

from boto.s3.key import Key
from django.core.files.uploadedfile import InMemoryUploadedFile, \
    TemporaryUploadedFile
from bson.objectid import ObjectId


__all__ = ['MketImageProcessor']

_IMAGE_DATA_REGEX = re.compile('data:image/(png|jpeg|jpg|gif|png);(base64),(.*)$')


class ImageOpener(object):
    @classmethod
    def open(cls, data):
        """
        @param data: it can be a image path or iplimage (opencv image)
        """
        if data and type(data) == str and os.path.exists(data):
            image = Image.open(data, 'r')
            try:
                image.verify()
            except:
                return None
            finally:
                image = Image.open(data, 'r')
        return image

    @classmethod
    def open_string(cls, stringData, encoding=None):
        if encoding:
            rawData = stringData.decode(encoding)

        try:
            image = Image.open(StringIO(rawData))
        except IOError:
            return None
        # verify image
        # after running verification method,
        # must reload image
        # if not, exception will be raised.
        try:
            image.verify()
        except:
            return None
        return Image.open(StringIO(rawData))

    @classmethod
    def open_encoded_data(cls, encoded_image_data):
        m = _IMAGE_DATA_REGEX.match(encoded_image_data).groups()
        extension = m[0]
        encoding = m[1]
        rawData = m[2].decode(encoding)
        pilImage = cls.open_string(rawData)
        return extension, encoding, pilImage

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


class MketImageResizer(object):
    @classmethod
    def resize(cls, pilImage, reqWidth, reqHeight=-1, centerCrop=False, overSize=False):
        """
        This method attemps to resize and crop the pilImage
        @param centerCrop: if True crops an image
        @parma overSize: if True, the resized image can be bigger and lager than the original image
        @return: pilImage
        """
        width, height = pilImage.size
        if not reqHeight or reqHeight <= 0:
            reqHeight = int(reqWidth * height / width)

        if not overSize:
            if reqWidth >= width:
                reqWidth = width;
            if reqHeight >= height:
                reqHeight = height

        widthForReqHeight = int(round(width * reqHeight / height))  # x : reqHeight = width : height
        heightForReqWidth = int(round(height * reqWidth / width))  # reqWidth : y = width : height

        if widthForReqHeight >= reqWidth:
            pilImage = pilImage.resize((widthForReqHeight, reqHeight), Image.ANTIALIAS)
            if centerCrop:
                pilImage = pilImage.crop(
                    (widthForReqHeight / 2 - reqWidth / 2, 0, widthForReqHeight / 2 + reqWidth / 2, reqHeight))
        else:
            pilImage = pilImage.resize((reqWidth, heightForReqWidth), Image.ANTIALIAS)
            if centerCrop:
                pilImage = pilImage.crop(
                    (0, heightForReqWidth / 2 - reqHeight / 2, reqWidth, heightForReqWidth / 2 + reqHeight / 2))
        return pilImage


class MketImage(ImageOpener):
    def __init__(self, image, format=None):
        """
        the constructor receives the image data by several means.
        @param image: PIL, image path, StringIO, IplImage etc....
        """
        self._image = None
        self.format = format

        # Set Image
        if isinstance(image, Image.Image):  # PIL
            self._image = image
        elif type(image) == str and os.path.exists(image):  # File Path
            self._image = ImageOpener.open(image)
        elif type(image) == str:  # Raw String Data
            self._image = ImageOpener.open_string(image)
        elif isinstance(image, InMemoryUploadedFile):
            self._image = ImageOpener.open_file(image)
        elif isinstance(image, TemporaryUploadedFile):
            self._image = ImageOpener.open_file(image)
        elif isinstance(image, MketImage):
            self._image = image._image
        elif image and hasattr(image, 'read'):
            self._image = ImageOpener.open_file(image)


        # Set Format
        if self._image and not format and hasattr(self._image, 'format') and self._image.format:
            self.format = self._image.format

        if not self._image or not self.format:
            raise ValueError(str(image) + " " + str(type(image)) + " cannot be instantiated")

    @property
    def size(self):
        return self._image.size

    def verify(self):
        if not self._image or not self.format:
            return False
        return True

    def resize(self, reqWidth, reqHeight=-1, centerCrop=False, overSize=False):
        self._image = MketImageResizer.resize(self._image, reqWidth, reqHeight, centerCrop, overSize)

    def clone(self):
        return MketImage(self._image.copy(), format=self.format)

    def save(self, to=None):
        if not to:
            to = self._create_filename()
        self._image.save(to)


    def _create_filename(self):
        while True:
            filename = str(ObjectId()) + "." + self.format.lower()
            if not os.path.exists(filename):
                return filename


class MketCloudImage(MketImage):
    """
    just Extending Class of MketImage.
    It supports interation with AWS S3
    """

    def __init__(self, image, bucket, format=None):
        super(MketCloudImage, self).__init__(image, format)
        # Set Bucket
        self._bucket = bucket
        # self._keyName = keyname # Key Name (Image File Name used on AWS S3)

    def clone(self):
        return MketCloudImage(self._image.copy(), bucket=self._bucket, format=self.format)

    def upload(self, keyname=None, prefix=None, public=True, reduced_redundancy=False):
        """
        Uploads the image to S3 Bucket.
        @param keyname: if the same keyname exists on the Bucket, then it automatically creates a new key name
        @param public: makes it public or not on the Bucket
        @return (key): newly created key
        """
        keyname = self.create_keyname(keyname, prefix)

        # Convert Image To StringIO
        output = StringIO()
        self._image.save(output, format=self.format)
        output.seek(0)

        # Upload the image to S3
        key = self._bucket.new_key(keyname)
        key.set_contents_from_file(output, reduced_redundancy=reduced_redundancy)
        if public:
            key.set_acl('public-read')

        output.close()
        return key

    def create_keyname(self, keyname=None, prefix=None):
        # Check if the default key can be used or not
        if keyname and not self._bucket.get_key(keyname):
            return keyname

        # Create a new Key Name
        while True:
            keyname = str(ObjectId()) + "." + self.format.lower()
            if prefix:
                keyname = os.path.join(prefix, keyname)
            if not self._bucket.get_key(keyname):
                return keyname
        return None

    @classmethod
    def get_url(cls, key, expire=0):
        if type(key) != Key:
            return None
        if not expire or expire <= 0:
            return key.generate_url(expires_in=expire, query_auth=False)
        return key.generate_url(expires_in=expire)
