from __future__ import absolute_import, print_function, division

import re
from unittest import TestCase
from six import BytesIO

from webtest import TestApp

from PIL import Image

from ..images import files
from ..images.view import MissingOriginal
from ..templating.renderer import MakoRenderingException

from . import utils


def setup():
    utils.load_images()


class Functional(TestCase):
    settings = None

    def setUp(self):
        self.app = TestApp(utils.make_app(self.settings))


class TestTemplatingFunctional(Functional):
    def test_render_index(self):
        resp = self.app.get('/')
        resp.mustcontain('base theme base.html')
        resp.mustcontain('foo theme base.html')
        resp.mustcontain('base theme index.html')

    def test_render_bad_return(self):
        with self.assertRaises(ValueError):
            self.app.get('/bad-return')

    def test_render_bad_template(self):
        with self.assertRaises(MakoRenderingException) as e:
            self.app.get('/bad-template')
        self.assertIn('dummy error', repr(e.exception))

    def test_render_text_escaping(self):
        resp = self.app.get('/text-template')
        resp.mustcontain('should not be escaped: <foo>')
        resp.mustcontain('should be escaped: &lt;foo&gt;')


class TestThemeStrategy(Functional):
    def setUp(self):
        def theme_strategy(req):
            return req.params.get('theme', 'foo')
        self.app = TestApp(utils.make_app(theme_strategy=theme_strategy))

    def test_render_alternate_theme(self):
        resp = self.app.get('/?theme=base')
        self.assertIn(b'base', resp.body)
        self.assertNotIn(b'foo', resp.body)

        resp = self.app.get('/?theme=foo')
        self.assertIn(b'base', resp.body)
        self.assertIn(b'foo', resp.body)


class TestAssetsFunctional(Functional):
    def test_js_tag(self):
        resp = self.app.get('/js-tag')
        resp.mustcontain('main.js')
        resp.mustcontain('require.js')

    def test_css__tag(self):
        resp = self.app.get('/css-tag')
        resp.mustcontain('main.less')
        resp.mustcontain('less.js')

    def test_svg_tag(self):
        resp = self.app.get('/svg-tag')
        resp.mustcontain('logo.svg')
        resp.mustcontain('img')


class TestCompiledFunctional(Functional):
    settings = {
        'pyramid_frontend.compile': True,
    }

    def setUp(self):
        Functional.setUp(self)
        utils.compile_assets()

    def test_js_tag(self):
        resp = self.app.get('/js-tag')
        body = resp.body.decode('utf-8')
        self.assertNotIn('require.js', body)
        # Look for something that looks like a hex digest
        self.assertRegexpMatches(body, '[a-f0-9]{8,}')
        # Fetch a second time to test caching and make sure it's the same
        # result.
        resp2 = self.app.get('/js-tag')
        body2 = resp2.body.decode('utf-8')
        self.assertEqual(body, body2)

        # Extract the filepath and load it.
        m = re.search('src="([^\"]+)"', body)
        path = m.group(1)
        file_resp = self.app.get(path)
        self.assertGreater(len(file_resp.body), 0)

    def test_css_tag(self):
        resp = self.app.get('/css-tag')
        body = resp.body.decode('utf-8')
        self.assertNotIn('less.js', body)
        # Look for something that looks like a hex digest
        self.assertRegexpMatches(body, '[a-f0-9]{8,}')

        # Extract the filepath and load it.
        m = re.search('href="([^\"]+)"', body)
        path = m.group(1)
        file_resp = self.app.get(path)
        self.assertGreater(len(file_resp.body), 0)

    def test_svg_tag(self):
        resp = self.app.get('/svg-tag')
        resp.mustcontain('img')

        # FIXME Check for minification and stuff, loading file path.


class TestImagesFunctional(Functional):
    def setUp(self):
        self.app = TestApp(utils.make_app())

    def test_fetch_image(self):
        url_resp = self.app.get('/image-url')
        img_resp = self.app.get(url_resp.body.decode('utf-8'))
        # This image should be 200x200
        f = BytesIO(img_resp.body)
        im = Image.open(f)
        self.assertEqual(im.size, (200, 200))

    def test_qualified_image_url(self):
        url_resp = self.app.get('/image-url')
        qual_resp = self.app.get('/image-url?qualified=1')
        self.assertTrue(qual_resp.body.endswith(url_resp.body))
        self.assertTrue(qual_resp.body.startswith(b'http://'))

    def test_image_url_theme(self):
        self.app.get('/image-url?filter_key=full')

        with self.assertRaises(AssertionError):
            self.app.get('/image-url?filter_key=barthumb')

    def test_image_tag(self):
        url_resp = self.app.get('/image-url')
        tag_resp = self.app.get('/image-tag')
        tag_resp.mustcontain('200')
        tag_resp.mustcontain('height')
        tag_resp.mustcontain('width')
        tag_resp.mustcontain('width')
        tag_resp.mustcontain(url_resp.body)

    def test_image_original_path(self):
        resp = self.app.get('/image-original-path')
        resp.mustcontain('originals')

    def test_fetch_image_bad_prefix(self):
        self.app.get('/img/aaaa/smiley-jpeg-rgb_jpg_thumb.png', status=404)

    def test_fetch_image_bad_suffix(self):
        name = 'smiley-jpeg-rgb'
        prefix = files.prefix_for_name(name)
        self.app.get('/img/%s/%s_jpg_nonexistent.png' % (prefix, name),
                     status=404)

    def test_fetch_image_bad_extension(self):
        name = 'smiley-jpeg-rgb'
        prefix = files.prefix_for_name(name)
        self.app.get('/img/%s/%s_doc_thumb.png' % (prefix, name),
                     status=404)

    def test_fetch_twice(self):
        name = 'smiley-jpeg-rgb'
        prefix = files.prefix_for_name(name)
        resp_a = self.app.get('/img/%s/%s_jpg_thumb.png' % (prefix, name))
        # FIXME This should try to find a way to test that it's fetching from
        # the filesystem the second time.
        resp_b = self.app.get('/img/%s/%s_jpg_thumb.png' % (prefix, name))
        self.assertEqual(resp_a.body, resp_b.body)

    def test_fetch_missing_original(self):
        name = 'nonexistent-file'
        prefix = files.prefix_for_name(name)
        with self.assertRaises(MissingOriginal):
            self.app.get('/img/%s/%s_jpg_thumb.png' % (prefix, name))

    def test_fetch_malformed_url(self):
        name = 'smiley-jpeg-rgb'
        prefix = files.prefix_for_name(name)
        self.app.get('/img/%s/%s_thumb.png' % (prefix, name), status=404)


class TestImagesDebug(Functional):
    def setUp(self):
        settings = {
            'pyramid_frontend.debug': 'true',
        }
        self.app = TestApp(utils.make_app(settings))

    def test_fetch_missing_original_placeholder(self):
        name = 'nonexistent-file'
        prefix = files.prefix_for_name(name)
        img_resp = self.app.get('/img/%s/%s_jpg_thumb.png' % (prefix, name))
        f = BytesIO(img_resp.body)
        im = Image.open(f)
        self.assertEqual(im.size, (200, 200))
