from __future__ import absolute_import, print_function, division

import os
import os.path
import pkg_resources

from unittest import TestCase

from PIL import Image

from ..images import filters

samples_dir = pkg_resources.resource_filename('pyramid_frontend.tests', 'data')


def filesize(f):
    orig_pos = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(orig_pos)
    return size


class TestFilters(TestCase):
    def assertSimilarColor(self, a, b, threshold=20):
        # Check manhattan distance
        if hasattr(a, '__len__'):
            dist = sum(abs(x - y) for x, y in zip(a, b))
        else:
            dist = abs(a - b)
        self.assertLess(dist, threshold)

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

    def test_png_save_alpha_palette(self):
        saver = filters.PNGSaver(palette=True)
        im = Image.new("RGBA", (25, 25), (255, 0, 0))
        im.putpixel((10, 10), (0, 255, 0))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, "P")
        converted = nm.convert('RGB')
        self.assertEqual(converted.getpixel((10, 10)), (0, 255, 0))

    def test_png_save_monochrome(self):
        saver = filters.PNGSaver()
        im = Image.new('L', (25, 25), 127)
        im.putpixel((10, 10), 255)

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertEqual(nm.getpixel((10, 10)), (255, 255, 255))

    def test_png_postprocess(self):
        saver = filters.PNGSaver()
        processor = filters.PNGProcessor()
        im = Image.new("RGBA", (25, 25), (255, 0, 0))
        im.putpixel((10, 10), (0, 255, 0))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, "RGBA")
        self.assertEqual(nm.getpixel((10, 10)), (0, 255, 0, 255))

        size_before = filesize(f)

        f = processor(f)
        size_after = filesize(f)

        self.assertGreater(size_after, 0)
        self.assertLessEqual(size_after, size_before)

        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGBA')
        self.assertEqual(nm.size, (25, 25))

    def test_png_save_sharpen(self):
        saver = filters.PNGSaver(sharpness=1.5)
        im = Image.new('RGBA', (25, 25), 'white')
        im.putpixel((10, 10), (255, 127, 127, 127))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGBA')
        self.assertEqual(nm.getpixel((10, 10)), (255, 88, 88, 127))

    def test_file_save(self):
        saver = filters.PNGSaver()
        f = open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'), 'rb')
        f = saver(f)

        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertEqual(nm.size, (512, 512))

    def test_jpeg_save(self):
        saver = filters.JPGSaver()
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        f = saver(im)

        nm = Image.open(f)
        self.assertEqual(nm.mode, "RGB")
        self.assertEqual(nm.getpixel((300, 300)), (206, 205, 1))

    def test_jpeg_save_low_quality(self):
        saver = filters.JPGSaver(quality=20)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        f = saver(im)

        # Should be less than 20K or so.
        self.assertLess(filesize(f), 20000)

    def test_jpeg_cmyk_save_png(self):
        saver = filters.PNGSaver()
        f = open(os.path.join(samples_dir, 'smiley-jpeg-cmyk.jpg'), 'rb')
        f = saver(f)

        nm = Image.open(f)
        self.assertEqual(nm.mode, "RGB")
        self.assertEqual(nm.size, (512, 512))

    def test_jpeg_cmyk_load_directly(self):
        # TODO May want to change this behavior at some point, and handle this
        # case.
        saver = filters.PNGSaver()
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-cmyk.jpg'))

        with self.assertRaises(AssertionError):
            saver(im)

    def test_jpeg_save_alpha(self):
        saver = filters.JPGSaver(quality=95)
        im = Image.new('RGBA', (30, 30), (255, 0, 0, 0))
        rect = Image.new('RGBA', (10, 10), (0, 255, 0, 255))
        im.paste(rect, (10, 10))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertSimilarColor(nm.getpixel((15, 15)), (0, 255, 0))

    def test_jpeg_save_monochrome(self):
        saver = filters.JPGSaver(quality=95)
        im = Image.new('L', (30, 30), 255)
        rect = Image.new('L', (10, 10), 0)
        im.paste(rect, (10, 10))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertEqual(nm.getpixel((15, 15)), (0, 0, 0))

    def test_jpeg_postprocess(self):
        saver = filters.JPGSaver()
        processor = filters.JPGProcessor()
        im = Image.new("RGB", (25, 25), (255, 0, 0))
        im.putpixel((10, 10), (0, 255, 0))

        f = saver(im)
        size_before = filesize(f)

        f = processor(f)
        size_after = filesize(f)

        self.assertGreater(size_after, 0)
        self.assertLessEqual(size_after, size_before)

        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertEqual(nm.size, (25, 25))

    def test_jpeg_save_sharpen(self):
        saver = filters.JPGSaver(sharpness=1.5)
        im = Image.new('RGB', (30, 30), 'white')
        rect = Image.new('RGB', (10, 10), (255, 0, 0))
        im.paste(rect, (10, 10))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertSimilarColor(nm.getpixel((15, 15)), (254, 6, 0))

    def test_vignette_filter(self):
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        filter = filters.VignetteFilter()
        saver = filters.JPGSaver()

        im = filter(im)
        f = saver(im)

        nm = Image.open(f)
        self.assertNotEqual(nm.getpixel((0, 0)), (255, 255, 255))

    def test_thumb_filter_defaults(self):
        filter = filters.ThumbFilter((64, 32))
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        self.assertEqual(im.size, (32, 32))

    def test_thumb_filter_crop(self):
        filter = filters.ThumbFilter((64, 32), crop=True)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        self.assertEqual(im.size, (64, 32))

    def test_thumb_filter_pad(self):
        filter = filters.ThumbFilter((64, 32), pad=True)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        self.assertEqual(im.size, (64, 32))

    def test_thumb_filter_crop_nonwhite(self):
        filter = filters.ThumbFilter((64, 32), crop='nonwhite')
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        # This test image has a white background, so it should just get
        # resized, and not cropped.
        self.assertEqual(im.size, (32, 32))

    def test_thumb_filter_crop_nonwhite_background(self):
        filter = filters.ThumbFilter((64, 32), crop='nonwhite')
        im = Image.new('RGB', (100, 100), 'red')
        im = filter(im)
        # This test image has a nonwhite background, so it should get cropped.
        self.assertEqual(im.size, (64, 32))

    def test_thumb_filter_crop_whitespace(self):
        filter = filters.ThumbFilter((64, 32), crop_whitespace=True)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        self.assertEqual(im.size, (32, 32))

    def test_thumb_filter_enlarge(self):
        filter = filters.ThumbFilter((1000, 1000), enlarge=True)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        self.assertEqual(im.size, (1000, 1000))

    def test_thumb_filter_unspecified_dims(self):
        filter = filters.ThumbFilter((None, None), crop_whitespace=True)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        self.assertEqual(im.size, (488, 488))

    def test_thumb_filter_unspecified_width(self):
        filter = filters.ThumbFilter((None, 100), crop_whitespace=True)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        self.assertEqual(im.size, (100, 100))

    def test_thumb_filter_unspecified_height(self):
        filter = filters.ThumbFilter((200, None), crop_whitespace=True)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        im = filter(im)
        self.assertEqual(im.size, (200, 200))
