from __future__ import absolute_import, print_function, division

import os.path
import pkg_resources

from unittest import TestCase

from ..images import files

from . import utils

samples_dir = pkg_resources.resource_filename('pyramid_frontend.tests', 'data')


class TestFiles(TestCase):
    def test_check_bad(self):
        f = open(os.path.join(samples_dir, 'not-an-image.png'), 'rb')
        with self.assertRaises(IOError):
            files.check(f)

    def test_check_good(self):
        f = open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'), 'rb')
        files.check(f)

    def test_save_to_error_dir(self):
        name = 'not-an-image.png'
        f = open(os.path.join(samples_dir, name), 'rb')
        error_dir = os.path.join(utils.work_dir, 'errors')
        settings = {
            'pyramid_frontend.error_dir': error_dir,
        }
        files.save_to_error_dir(settings, name, f)
        # Saving same file twice should work
        files.save_to_error_dir(settings, '2.png', f)

    def test_check_and_save_image_bad(self):
        f = open(os.path.join(samples_dir, 'not-an-image.png'), 'rb')
        error_dir = os.path.join(utils.work_dir, 'errors')
        settings = {
            'pyramid_frontend.error_dir': error_dir,
        }
        with self.assertRaises(IOError):
            files.check_and_save_image(settings, 'not-an-image', f)

    def test_check_and_save_image_good(self):
        f = open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'), 'rb')
        originals_dir = os.path.join(utils.work_dir, 'originals')
        settings = {
            'pyramid_frontend.original_image_dir': originals_dir,
        }
        info = files.check_and_save_image(settings, 'smiley-jpeg-rgb', f)
        self.assertEqual(info['ext'], 'jpg')
        self.assertEqual(info['size'], (512, 512))
