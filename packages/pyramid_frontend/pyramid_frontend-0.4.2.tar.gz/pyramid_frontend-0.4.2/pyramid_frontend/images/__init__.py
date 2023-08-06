from __future__ import absolute_import, print_function, division

from webhelpers2.html.tags import HTML

from .files import (prefix_for_name, get_url_prefix, original_path,
                    save_image, save_to_error_dir, check, filter_sep)
from .view import ImageView, MissingOriginal
from .chain import PassThroughFilterChain, FilterChain

__all__ = ['FilterChain', 'MissingOriginal',
           'save_image', 'save_to_error_dir', 'check', 'filter_sep']


def add_image_filter(config, chain, with_theme=None):
    """
    Pyramid config directive to register an image filter chain.
    """
    def register(with_theme):
        registry = config.registry

        if not hasattr(registry, 'image_filter_registry'):
            registry.image_filter_registry = {}
        filter_registry = registry.image_filter_registry

        if chain.suffix in filter_registry:
            registered_chain, registered_theme_set = \
                filter_registry[chain.suffix]
            if registered_chain != chain:
                raise ValueError(
                    "suffix %r already registered with different instance" %
                    chain.suffix)
            registered_theme_set.add(with_theme)
        else:
            with_theme_set = set()
            if with_theme:
                with_theme_set.add(with_theme)
            filter_registry[chain.suffix] = (chain, with_theme_set)

    intr = config.introspectable(category_name='image_filters',
                                 discriminator=chain.suffix,
                                 title=chain.suffix,
                                 type_name=None)
    intr['chain'] = chain
    intr['with_theme'] = with_theme

    config.action(('image_filter', chain.suffix, with_theme),
                  register,
                  args=(with_theme,),
                  introspectables=(intr,))


def image_url(request, name, original_ext, filter_key,
              qualified=False, _scheme=None, _host=None, _port=None):
    """
    Return the URL for an image as processed by a specified image filter chain.
    """
    filter_registry = request.registry.image_filter_registry

    # Check if there is a theme active. If so, check that the supplied
    # filter_key is ref'd within the theme: if not, fail with a descriptive
    # exception.
    chain, with_theme_set = filter_registry[filter_key]
    if with_theme_set and getattr(request, 'theme', None):
        assert request.theme in with_theme_set, \
            ("current theme is %r, but this filter is only registered "
             "with %r" % (request.theme, with_theme_set))

    prefix = prefix_for_name(name)
    name = chain.basename(name, original_ext)
    if qualified:
        return request.route_url('pyramid_frontend:images',
                                 prefix=prefix,
                                 name=name,
                                 _scheme=_scheme or request.scheme,
                                 _host=_host or request.host,
                                 _port=_port or request.server_port)
    else:
        return request.route_path('pyramid_frontend:images',
                                  prefix=prefix,
                                  name=name)


def image_tag(request, name, original_ext, filter_key,
              qualified=False, _scheme=None, _host=None, _port=None, **kwargs):
    """
    Return the HTML tag for an image as processed by a specified image filter
    chain.
    """
    filter_registry = request.registry.image_filter_registry
    chain, with_theme = filter_registry[filter_key]

    kwargs.setdefault('width', chain.width)
    kwargs.setdefault('height', chain.height)

    url = request.image_url(name, original_ext, filter_key,
                            qualified=qualified, _scheme=_scheme, _host=_host)

    return HTML.img(src=url, **kwargs)


def image_original_path(request, name, original_ext):
    """
    Return the filesystem path for an original image.
    """
    settings = request.registry.settings
    return original_path(settings, name, original_ext)


def includeme(config):
    config.add_directive('add_image_filter', add_image_filter)
    config.add_image_filter(PassThroughFilterChain())

    config.add_request_method(image_url, 'image_url')
    config.add_request_method(image_tag, 'image_tag')
    config.add_request_method(image_original_path, 'image_original_path')

    url_prefix = get_url_prefix(config.registry.settings)
    config.add_route('pyramid_frontend:images',
                     '%s/{prefix}/{name:.+\.\w+}' % url_prefix)
    config.add_view(ImageView, route_name='pyramid_frontend:images')
