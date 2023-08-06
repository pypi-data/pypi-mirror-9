from __future__ import absolute_import, print_function, division

import os
import os.path
import shutil
import pkg_resources

from unittest import TestCase, skip

from PIL import Image

from ..images.chain import FilterChain, PassThroughFilterChain

from . import utils

samples_dir = pkg_resources.resource_filename('pyramid_frontend.tests', 'data')


class TestFilterChain(TestCase):
    work_dir = os.path.join(utils.work_dir, 'filter-chain-tests')
    test_files = ['smiley-jpeg-rgb.jpg',
                  'smiley-png24-alpha.png',
                  'smiley-gif-alpha.gif',
                  'smiley-jpeg-cmyk.jpg']

    def setUp(self):
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir)

    def test_basename(self):
        chain = FilterChain('thumb200', extension='png')
        self.assertEqual(chain.basename('some-cool-image', 'jpg'),
                         'some-cool-image_jpg_thumb200.png')
        self.assertEqual(chain.basename('delicious', 'gif'),
                         'delicious_gif_thumb200.png')

    def test_repr(self):
        chain = FilterChain('zygolicious', extension='png')
        self.assertIn('zygolicious', repr(chain))

    def test_basename_passthrough(self):
        chain = PassThroughFilterChain()
        self.assertEqual(chain.basename('some-cool-image', 'jpg'),
                         'some-cool-image.jpg')
        self.assertEqual(chain.basename('delicious', 'gif'),
                         'delicious.gif')

    def _process(self, chain, filename):
        orig_path = os.path.join(samples_dir, filename)
        image_data = open(orig_path, 'rb')
        proc_path = os.path.join(self.work_dir, filename)
        chain.run(proc_path, image_data)

        im = Image.open(proc_path)
        return im

    def _chain_basic(self, filename):
        chain = FilterChain('thumb50', extension='png',
                            width=50, height=50)
        im = self._process(chain, filename)
        self.assertEqual(im.size, (50, 50))

    def test_chain_basic_jpeg_rgb(self):
        self._chain_basic('smiley-jpeg-rgb.jpg')

    def test_chain_basic_jpeg_cmyk(self):
        self._chain_basic('smiley-jpeg-cmyk.jpg')

    def test_chain_basic_png(self):
        self._chain_basic('smiley-png24-alpha.png')

    # Pillow has broken GIF support in the versions that support py3k.
    @skip
    def test_chain_basic_gif(self):
        self._chain_basic('smiley-gif-alpha.gif')

    def _chain_passthrough(self, filename):
        chain = PassThroughFilterChain()
        im = self._process(chain, filename)
        self.assertEqual(im.size, (512, 512))

    def test_chain_passthrough_jpeg_rgb(self):
        self._chain_passthrough('smiley-jpeg-rgb.jpg')

    def test_chain_passthrough_jpeg_cmyk(self):
        self._chain_passthrough('smiley-jpeg-cmyk.jpg')

    def test_chain_passthrough_png(self):
        self._chain_passthrough('smiley-png24-alpha.png')

    def test_chain_passthrough_gif(self):
        self._chain_passthrough('smiley-gif-alpha.gif')

    def test_run_missing_output_dir(self):
        chain = FilterChain('thumb50', extension='png',
                            width=50, height=50)
        filename = self.test_files[0]
        orig_path = os.path.join(samples_dir, filename)
        image_data = open(orig_path, 'rb')
        proc_path = os.path.join(self.work_dir, 'blah', filename)
        chain.run(proc_path, image_data)
        im = Image.open(proc_path)
        self.assertEqual(im.size, (50, 50))

    def test_run_no_thumb(self):
        chain = FilterChain('thumbless', extension='png', no_thumb=True)
        im = self._process(chain, self.test_files[0])
        self.assertEqual(im.size, (512, 512))
