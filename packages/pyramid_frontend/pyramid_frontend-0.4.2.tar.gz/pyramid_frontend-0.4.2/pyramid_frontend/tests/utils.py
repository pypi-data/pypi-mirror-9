from __future__ import absolute_import, print_function, division

import pkg_resources
import os
import os.path
import glob
import shutil

from pyramid.config import Configurator

from pyramid_frontend.tests.example import base, foo, bar
from pyramid_frontend.images.files import check_and_save_image
from pyramid_frontend.images.chain import FilterChain

from .. import compile


samples_dir = pkg_resources.resource_filename('pyramid_frontend.tests', 'data')

test_ini_path = pkg_resources.resource_filename('pyramid_frontend.tests',
                                                'test.ini')

work_dir = '/tmp/pfe-test-workdir'


default_settings = {
    'pyramid_frontend.theme': 'foo',
    'pyramid_frontend.original_image_dir': os.path.join(work_dir, 'originals'),
    'pyramid_frontend.processed_image_dir': os.path.join(work_dir,
                                                         'processed'),
    'pyramid_frontend.compiled_asset_dir': os.path.join(work_dir, 'compiled'),
}


def noop_view(request):
    return {}


def bad_return_view(request):
    return 'not-a-dict'


def bad_template_view(request):
    return {}


def image_url_view(request):
    filter_key = request.params.get('filter_key', 'thumb')
    qualified = bool(request.params.get('qualified'))
    return request.image_url('smiley-jpeg-rgb', 'jpg', filter_key,
                             qualified=qualified)


def image_tag_view(request):
    filter_key = request.params.get('filter_key', 'thumb')
    return request.image_tag('smiley-jpeg-rgb', 'jpg', filter_key)


def image_original_path_view(request):
    return request.image_original_path('smiley-jpeg-rgb', 'jpg')


def js_tag_view(request):
    return request.asset_tag('main-js')


def css_tag_view(request):
    return request.asset_tag('main-less')


def svg_tag_view(request):
    return request.asset_tag('logo-svg')


def load_images(settings=default_settings):
    """
    Load images from test 'samples' directory to originals dir.
    """
    originals = settings['pyramid_frontend.original_image_dir']
    processed = settings['pyramid_frontend.processed_image_dir']
    if os.path.exists(originals):
        shutil.rmtree(originals)
    if os.path.exists(processed):
        shutil.rmtree(processed)
    os.makedirs(originals)
    os.makedirs(processed)

    for filename in glob.glob(os.path.join(samples_dir, '*.*')):
        f = open(filename, 'rb')
        name, raw_ext = os.path.basename(filename).rsplit('.', 1)
        if name != 'not-an-image':
            check_and_save_image(settings, name, f)


def make_app(settings=None, theme_strategy=None):
    base_settings = default_settings.copy()
    if settings:
        base_settings.update(settings)
    config = Configurator(settings=base_settings)

    config.include('pyramid_frontend')

    config.add_image_filter(FilterChain('thumb', width=200, height=200,
                                        crop=True))

    config.add_theme(base.BaseTheme)
    config.add_theme(foo.FooTheme)
    config.add_theme(bar.BarTheme)

    config.add_route('index', '/')
    config.add_route('article', '/article')

    config.add_route('bad-return', '/bad-return')
    config.add_route('bad-template', '/bad-template')

    config.add_route('image-url', '/image-url')
    config.add_route('image-tag', '/image-tag')
    config.add_route('image-original-path', '/image-original-path')

    config.add_route('js-tag', '/js-tag')
    config.add_route('css-tag', '/css-tag')
    config.add_route('svg-tag', '/svg-tag')

    config.add_route('text-template', '/text-template')

    config.add_view(noop_view, route_name='index', renderer='index.html')
    config.add_view(noop_view, route_name='article', renderer='article.html')

    config.add_view(bad_return_view, route_name='bad-return',
                    renderer='index.html')
    config.add_view(bad_template_view, route_name='bad-template',
                    renderer='bad.html')

    config.add_view(image_url_view, route_name='image-url', renderer='string')
    config.add_view(image_tag_view, route_name='image-tag', renderer='string')
    config.add_view(image_original_path_view, route_name='image-original-path',
                    renderer='string')

    config.add_view(js_tag_view, route_name='js-tag', renderer='string')
    config.add_view(css_tag_view, route_name='css-tag', renderer='string')
    config.add_view(svg_tag_view, route_name='svg-tag', renderer='string')

    config.add_view(noop_view, route_name='text-template',
                    renderer='text-template.txt')

    if theme_strategy:
        config.set_theme_strategy(theme_strategy)

    return config.make_wsgi_app()


def app_factory(global_config, **local_conf):
    global_config.update(local_conf)
    return make_app(global_config)


def compile_assets():
    args = ['pcompile', test_ini_path]
    return compile.main(args)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    app = make_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
