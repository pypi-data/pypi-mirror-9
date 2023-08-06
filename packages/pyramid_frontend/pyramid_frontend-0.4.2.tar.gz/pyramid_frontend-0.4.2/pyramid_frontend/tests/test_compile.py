from __future__ import absolute_import, print_function, division

import os.path
import subprocess
from mock import patch
from unittest import TestCase
from six import StringIO

from .. import compile
from ..assets.asset import Asset
from ..assets.less import LessAsset
from ..assets.requirejs import RequireJSAsset
from ..assets.svg import SVGAsset

from . import utils
from .example import foo


class TestCompileCommand(TestCase):

    def test_pcompile_usage(self):
        args = [
            'pcompile',
        ]
        buf = StringIO()
        with patch('sys.stderr', buf):
            with self.assertRaises(SystemExit) as cm:
                compile.main(args)
            exit_exception = cm.exception
            self.assertEqual(exit_exception.code, 2)
        self.assertIn('config_uri', buf.getvalue())

    def test_pcompile(self):
        args = ['pcompile', utils.test_ini_path]
        retcode = compile.main(args)
        self.assertEqual(retcode, 0)

    def test_pcompile_no_minify(self):
        args = ['pcompile', utils.test_ini_path, '--no-minify']
        retcode = compile.main(args)
        self.assertEqual(retcode, 0)
        # XXX Try to assett hat this makes longer assets or something.


class TestAsset(TestCase):
    def setUp(self):
        self.theme = foo.FooTheme({})
        self.output_dir = os.path.join(utils.work_dir, 'compile-tests')

    def test_bad_shell(self):
        asset = Asset(None)
        buf = StringIO()
        with patch('sys.stdout', buf):
            with self.assertRaises(subprocess.CalledProcessError):
                argv = [
                    'false',
                ]
                asset.run_command(argv)
        # XXX Try to test that this actually prints the stdout output of a
        # failed comamnd.

    def test_less_compile(self):
        asset = LessAsset('/_foo/css/main.less')
        path = asset.compile(key='main-less',
                             theme=self.theme,
                             output_dir=self.output_dir)
        f = open(path, 'rb')
        buf_minified = f.read()
        self.assertGreater(len(buf_minified), 0)

        # Test that minified version is smaller than non-minified.
        asset = LessAsset('/_foo/css/main.less')
        path = asset.compile(key='main-less',
                             theme=self.theme,
                             output_dir=self.output_dir,
                             minify=False)
        f = open(path, 'rb')
        buf_unminified = f.read()

        self.assertLess(len(buf_minified), len(buf_unminified))

    def test_requirejs_compile(self):
        asset = RequireJSAsset('/_foo/js/main.js')
        path = asset.compile(key='main-js',
                             theme=self.theme,
                             output_dir=self.output_dir)
        f = open(path, 'rb')
        buf_minified = f.read()
        self.assertGreater(len(buf_minified), 0)

        # Test that minified version is smaller than non-minified.
        asset = RequireJSAsset('/_foo/js/main.js')
        path = asset.compile(key='main-js',
                             theme=self.theme,
                             output_dir=self.output_dir,
                             minify=False)
        f = open(path, 'rb')
        buf_unminified = f.read()

        self.assertLess(len(buf_minified), len(buf_unminified))

    def test_svg_compile(self):
        asset = SVGAsset('/_foo/images/logo.svg')
        path = asset.compile(key='logo-svg',
                             theme=self.theme,
                             output_dir=self.output_dir)
        f = open(path, 'r')
        buf = f.read()
        self.assertGreater(len(buf), 0)
        self.assertIn('svg', buf)
