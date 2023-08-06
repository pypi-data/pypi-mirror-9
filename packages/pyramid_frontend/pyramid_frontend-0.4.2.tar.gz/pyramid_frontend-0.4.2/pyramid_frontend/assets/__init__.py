from __future__ import absolute_import, print_function, division

from webhelpers2.html.tags import literal
from pyramid.settings import asbool


def asset_tag(request, key, **kwargs):
    """
    Request method to render an HTML fragment containing tags which reference
    the supplied entry point. This will dispatch to the appropriate tag
    rendering function based on context and entry point type.
    """
    theme = request.theme
    asset = theme.stacked_assets[key]
    settings = request.registry.settings
    should_compile = asbool(settings.get('pyramid_frontend.compile'))

    if should_compile:
        filename = theme.compiled_asset_path(key)
        url_path = '/compiled/' + theme.key + '/' + filename
    else:
        url_path = asset.url_path

    return literal(asset.tag(theme, url_path, production=should_compile,
                             **kwargs))


def includeme(config):
    config.add_request_method(asset_tag, 'asset_tag')

    compiled_path = \
        config.registry.settings['pyramid_frontend.compiled_asset_dir']
    config.add_static_view(name='compiled', path=compiled_path)
