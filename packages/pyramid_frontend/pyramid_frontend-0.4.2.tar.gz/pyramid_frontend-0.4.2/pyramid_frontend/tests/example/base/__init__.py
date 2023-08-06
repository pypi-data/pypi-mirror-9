from __future__ import absolute_import, print_function, division

from pyramid_frontend.theme import Theme
from pyramid_frontend.images.chain import FilterChain
from pyramid_frontend.assets.less import LessAsset


def base_includeme(config):
    test_includes = config.registry.settings.setdefault('test_includes', [])
    test_includes.append('base')


class BaseTheme(Theme):
    key = 'base'
    image_filters = [
        FilterChain('full', width=400, height=400, crop=True),
    ]
    assets = {
        'main-less': LessAsset('/_base/css/main.less'),
    }
    includes = [
        base_includeme,
    ]
