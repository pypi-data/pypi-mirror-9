from __future__ import absolute_import, print_function, division

import os.path
from unittest import TestCase

from mako.exceptions import TopLevelLookupException
from mako.runtime import Context
from mako.util import FastEncodingBuffer

from ..templating.lookup import SuperTemplateLookup

from .example import base, foo, quux


class TestThemeLookup(TestCase):
    settings = {
        'pyramid_frontend.compiled_asset_dir': '.'
    }

    def test_render_foo_index(self):
        theme = foo.FooTheme(self.settings)
        templ = theme.lookup.get_template('index.html')
        s = templ.render()
        self.assertIn(b'base theme base.html', s)
        self.assertIn(b'foo theme base.html', s)
        self.assertIn(b'base theme index.html', s)
        self.assertNotIn(b'bar', s)

        self.assertIn(b'foo theme blocks header', s)

    def test_render_foo_article(self):
        theme = foo.FooTheme(self.settings)
        templ = theme.lookup.get_template('article.html')
        s = templ.render()
        self.assertIn(b'base theme base.html', s)
        self.assertIn(b'foo theme base.html', s)
        self.assertIn(b'foo theme article.html', s)
        self.assertNotIn(b'bar', s)

        self.assertIn(b'foo theme blocks header', s)

    def test_render_base_index(self):
        theme = base.BaseTheme(self.settings)
        templ = theme.lookup.get_template('index.html')
        s = templ.render()
        self.assertIn(b'base theme base.html', s)
        self.assertIn(b'base theme index.html', s)
        self.assertNotIn(b'foo', s)
        self.assertNotIn(b'bar', s)

        self.assertIn(b'base theme blocks header', s)

    def test_render_base_article(self):
        theme = base.BaseTheme(self.settings)
        templ = theme.lookup.get_template('article.html')
        s = templ.render()
        self.assertIn(b'base theme base.html', s)
        self.assertIn(b'base theme article.html', s)
        self.assertNotIn(b'foo', s)

        self.assertIn(b'base theme blocks header', s)

    def test_render_quux_article(self):
        theme = quux.QuuxTheme(self.settings)
        templ = theme.lookup.get_template('article.html')
        s = templ.render()
        self.assertIn(b'base theme base.html', s)
        self.assertIn(b'foo theme base.html', s)
        self.assertIn(b'foo theme article.html', s)

        self.assertIn(b'quux theme blocks header', s)

    def test_render_missing_template(self):
        theme = foo.FooTheme(self.settings)
        with self.assertRaises(TopLevelLookupException):
            theme.lookup.get_template('nonexistent-template.html')

    def test_find_dir_for(self):
        theme = foo.FooTheme(self.settings)
        with self.assertRaises(ValueError):
            theme.lookup.find_dir_for_path('/some/other/path.html')

    def test_render_text(self):
        theme = foo.FooTheme(self.settings)
        templ = theme.lookup_nofilters.get_template('article.txt')
        s = templ.render()
        self.assertIn(b'foo theme article.txt', s)
        self.assertIn(b'this should not be escaped: <>', s)

    def test_render_text_unicode(self):
        theme = foo.FooTheme(self.settings)
        templ = theme.lookup_nofilters.get_template('unicode.txt')
        s = templ.render()
        self.assertIn(b'foo theme unicode.txt', s)
        self.assertIn(u'this is unicode: \u2603'.encode('utf8'), s)

    def test_get_def_base(self):
        theme = base.BaseTheme(self.settings)
        templ = theme.lookup.get_template('common/blocks.html')
        buf = FastEncodingBuffer(as_unicode=True)
        ctx = Context(buf)
        templ.get_def('hello').render_context(ctx)

        s = buf.getvalue()
        self.assertIn('base theme blocks hello', s)

    def test_get_def_by_file(self):
        theme = quux.QuuxTheme(self.settings)

        filename = os.path.join(theme.template_dirs[1], 'common/blocks.html')
        uri = theme.lookup.filename_to_uri(filename)

        templ = theme.lookup.get_template(uri)

        buf = FastEncodingBuffer(as_unicode=True)
        ctx = Context(buf)
        templ.get_def('hello').render_context(ctx)

        s = buf.getvalue()
        self.assertIn('foo theme blocks hello', s)


class TestLookupOptions(TestCase):
    settings = {
        'pyramid_frontend.compiled_asset_dir': '.'
    }

    def test_filesystem_checks(self):
        theme = foo.FooTheme(self.settings)
        dirs = theme.lookup.directories
        lookup = SuperTemplateLookup(directories=dirs,
                                     filesystem_checks=True)
        templ = lookup.get_template('index.html')
        s = templ.render()
        self.assertIn('foo theme', s)
