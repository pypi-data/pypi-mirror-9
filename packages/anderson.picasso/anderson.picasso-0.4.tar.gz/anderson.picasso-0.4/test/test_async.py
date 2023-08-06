# -*- coding:utf-8 -*-
from PIL import Image
import os
import re
import unittest
from picasso.api import Picasso, PicassoManager

image_regex = re.compile('\.(jpg|png|gif)$', flags=re.IGNORECASE)


class PicassoAsyncTest(unittest.TestCase):
    def setUp(self):
        self.delete_images()

    def tearDown(self):
        self.delete_images()

    def delete_images(self):
        for n in os.listdir('test'):
            if image_regex.search(n) and n not in ['height.jpg', 'width.jpg']:
                os.remove(os.path.join('test', n))

    def test_async(self):
        def callback(picasso):
            self.assertTrue(picasso)
            self.assertEqual((640, 960), picasso.size)

        picasso = Picasso()
        picasso.open('test/height.jpg')

        manager = PicassoManager()
        manager.put(picasso, callback)
        manager.join()


        def callback(picasso):
            self.assertEqual((200, 200), picasso.size)
            picasso.save('test/async.jpg')

            image = Image.open('test/async.jpg')
            self.assertEqual((200, 200), image.size)

        picasso.open('test/width.jpg').resize(200, 200).centerCrop(True)
        manager.put(picasso, callback)
        manager.join()


    def test_args_and_kwargs(self):
        def callback(picasso, *args, **kwargs):
            self.assertTrue(picasso)
            self.assertEqual((640, 960), picasso.size)
            self.assertEqual((1, 2, 3), args)
            self.assertEqual({'please': 'God help me!'}, kwargs)

        picasso = Picasso()
        picasso.open('test/height.jpg')

        manager = PicassoManager()
        manager.put(picasso, callback, args=[1, 2, 3], kwargs={'please': 'God help me!'})
        manager.join()



