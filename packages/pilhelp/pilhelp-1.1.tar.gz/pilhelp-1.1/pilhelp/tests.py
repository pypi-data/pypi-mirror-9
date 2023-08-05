import unittest

from PIL import Image
import thumbnails


class ThumbnailTests(unittest.TestCase):

    def test_thumbnail_image_wide(self):
       img = Image.new("RGB", (640, 480))
       thumb = thumbnails.thumbnail(img, 300, 100)
       self.assertEquals((300, 100, ), thumb.size)
    
    def test_thumbnail_image_skyscraper(self):
        img = Image.new("RGB", (640, 480))
        thumb = thumbnails.thumbnail(img, 100, 300)
        self.assertEquals((100, 300, ), thumb.size)
  
    def test_thumbnail_image_square(self):
        img = Image.new("RGB", (640, 480))
        thumb = thumbnails.thumbnail(img, 300, 300)
        self.assertEquals((300, 300, ), thumb.size)

    def test_thumbnail_huger_than_original(self):
        img = Image.new("RGB", (160, 120))
        thumb = thumbnails.thumbnail(img, 300, 100)
        self.assertEquals((300, 100, ), thumb.size)

