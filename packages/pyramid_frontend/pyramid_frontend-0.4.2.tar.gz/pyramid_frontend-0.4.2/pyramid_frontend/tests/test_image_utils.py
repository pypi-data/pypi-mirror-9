from __future__ import absolute_import, print_function, division

import os.path
import pkg_resources

from unittest import TestCase

from PIL import Image

from ..images import utils, filters

samples_dir = pkg_resources.resource_filename('pyramid_frontend.tests', 'data')


class TestUtils(TestCase):
    def setUp(self):
        self.im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))

    def test_bounding_box(self):
        self.assertEqual(utils.bounding_box(self.im), (8, 16, 496, 504))

    def test_image_entropy(self):
        entropy = utils.image_entropy(self.im)
        self.assertAlmostEqual(entropy, 5.4, places=1)

    def test_is_larger(self):
        self.assertTrue(utils.is_larger(self.im, (200, 200)))
        self.assertFalse(utils.is_larger(self.im, (600, 600)))
        self.assertFalse(utils.is_larger(self.im, (512, 512)))

    def test_pad_image(self):
        padded = utils.pad_image(self.im, (600, 600))
        self.assertEqual(padded.size, (600, 600))

    def test_colors_differ(self):
        self.assertTrue(utils.colors_differ((127, 243, 100),
                                            (125, 243, 95),
                                            tolerance=5))
        self.assertFalse(utils.colors_differ((127, 243, 100),
                                             (125, 243, 95),
                                             tolerance=20))

    def test_crop_entropy_same(self):
        im = utils.crop_entropy(self.im, (300, 300))
        self.assertEqual(im.getpixel((150, 150)), (206, 205, 1))

    def test_crop_entropy_wide(self):
        im = utils.crop_entropy(self.im, (300, 100))
        self.assertEqual(im.getpixel((150, 50)), (202, 200, 1))

    def test_crop_entropy_tall(self):
        im = utils.crop_entropy(self.im, (100, 300))
        self.assertIn(im.getpixel((50, 150)), [(208, 208, 0),
                                               (209, 208, 0)])

    def test_is_white_background(self):
        self.assertTrue(utils.is_white_background(self.im))

        cropped = self.im.crop((0, 0, 256, 256))
        self.assertFalse(utils.is_white_background(cropped))
        cropped = self.im.crop((0, 256, 256, 512))
        self.assertFalse(utils.is_white_background(cropped))
        cropped = self.im.crop((0, 0, 256, 512))
        self.assertFalse(utils.is_white_background(cropped))
        cropped = self.im.crop((256, 0, 512, 512))
        self.assertFalse(utils.is_white_background(cropped))


class TestFilters(TestCase):
    def test_png_save_rgb(self):
        saver = filters.PNGSaver(palette=True)
        im = Image.new("RGB", (25, 25), "red")
        f = saver(im)

        nm = Image.open(f)
        self.assertEqual(nm.mode, "P")
        nm = nm.convert("RGBA")
        self.assertEqual(nm.getpixel((8, 8)), (255, 0, 0, 255))

    def test_png_save_palette(self):
        saver = filters.PNGSaver(palette=True)
        im = Image.new("P", (25, 25))
        im.putpalette([0] * 768)
        im.paste(23, (0, 0, 25, 25))
        f = saver(im)

        nm = Image.open(f)
        self.assertEqual(nm.mode, "P")
        self.assertEqual(nm.getpixel((8, 8)), 23)
