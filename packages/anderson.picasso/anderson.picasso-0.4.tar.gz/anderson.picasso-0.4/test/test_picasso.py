# -*- coding:utf-8 -*-
from PIL import Image
from StringIO import StringIO
import re
import os
import unittest
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile

from picasso.api import Picasso, get_picasso_manager, PicassoManager


image_regex = re.compile('\.(jpg|png|gif)$', flags=re.IGNORECASE)


class PicassoTest(unittest.TestCase):
    def setUp(self):
        self.delete_images()

    def tearDown(self):
        self.delete_images()

    def delete_images(self):
        for n in os.listdir('test'):
            if image_regex.search(n) and n not in ['height.jpg', 'width.jpg']:
                os.remove(os.path.join('test', n))

    def test_get_singleton(self):
        """
        피카소 매니져 싱글턴을 받는다
        """
        manager1 = get_picasso_manager()
        manager2 = get_picasso_manager()
        self.assertIs(manager1, manager2)
        self.assertIsNot(manager2, PicassoManager())

    def test_resize(self):
        """
        리싸이즈 테스트
        """
        picasso = Picasso()
        # 가로가 더 긴 이미지
        picasso.open('./test/width.jpg').resize(200, 200).execute()
        picasso.save('test/resized01.jpg')
        image = Image.open('test/resized01.jpg')
        self.assertEqual((320, 200), image.size)

        # 세로가 더 긴 이미지
        picasso.open('./test/height.jpg').resize(200, 200).execute()
        picasso.save('test/resized02.jpg')
        image = Image.open('test/resized02.jpg')
        self.assertEqual((200, 300), image.size)


    def test_centerCrop(self):
        """
        center crop 을 테스트한다.
        """
        picasso = Picasso()

        # 가로가 더 긴 이미지
        picasso.open('./test/width.jpg') \
            .resize(200, 200) \
            .centerCrop(True) \
            .execute() \
            .save('test/center_cropped01.jpg')

        image = Image.open('test/center_cropped01.jpg')
        self.assertEqual((200, 200), image.size)

        # 세로가 더 긴 이미지
        picasso.open('./test/height.jpg') \
            .resize(200, 200) \
            .centerCrop(True) \
            .execute() \
            .save('test/center_cropped02.jpg')

        image = Image.open('test/center_cropped02.jpg')
        self.assertEqual((200, 200), image.size)

    def test_open(self):
        """
        여러가지 리소스 이미지를 여는 테스트
        :return:
        """
        picasso = Picasso()

        # PIL Image
        image = Image.open('test/width.jpg')
        picasso.open(image).centerCrop(True).resize(100, 300).execute()
        picasso.save('test/open_pil.jpg')

        image = Image.open('test/open_pil.jpg')
        self.assertEqual((100, 300), image.size)

        # String IO
        io = StringIO()
        image = Image.open('test/height.jpg')
        image.save(io, image.format)

        io.seek(0)
        picasso.open(io).centerCrop(True).execute() # centerCrop만 하고 resize는 안함
        picasso.save('test/haha.jpg')

        # Django In Memory File
        io.seek(0)
        file = SimpleUploadedFile('hi', io.getvalue())
        picasso.open(file).resize(100, 100).execute()
        picasso.save('test/memory.jpg')

        image = Image.open('test/memory.jpg')
        self.assertEqual((100, 150), image.size)

    def test_to_stringIO(self):
        picasso = Picasso()
        picasso.open('test/width.jpg')
        io = picasso.to_stringIO()
        self.assertIsInstance(io, StringIO)













