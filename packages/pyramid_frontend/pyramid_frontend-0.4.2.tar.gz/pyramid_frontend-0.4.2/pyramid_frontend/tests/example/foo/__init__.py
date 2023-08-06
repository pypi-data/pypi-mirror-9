from __future__ import absolute_import, print_function, division

from ..base import BaseTheme
from pyramid_frontend.images.chain import FilterChain
from pyramid_frontend.assets.less import LessAsset
from pyramid_frontend.assets.requirejs import RequireJSAsset
from pyramid_frontend.assets.svg import SVGAsset


def foo_includeme(config):
    test_includes = config.registry.settings.setdefault('test_includes', [])
    test_includes.append('foo')


class FooTheme(BaseTheme):
    key = 'foo'
    image_filters = [
        FilterChain('tiny', width=64, height=64, crop=True),
    ]
    assets = {
        'main-less': LessAsset('/_foo/css/main.less'),
        'main-js': RequireJSAsset('/_foo/js/main.js'),
        'logo-svg': SVGAsset('/_foo/images/logo.svg'),
    }
    includes = [
        '.foo_includeme',
    ]
