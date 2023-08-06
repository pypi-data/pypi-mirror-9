from __future__ import absolute_import, print_function, division

import os.path
import inspect
import pkg_resources

from pyramid.decorator import reify
from pyramid.settings import aslist, asbool
from pyramid.path import DottedNameResolver

from .templating.lookup import SuperTemplateLookup
from .templating.renderer import (mako_renderer_factory,
                                  mako_renderer_factory_nofilters)

static_dir = pkg_resources.resource_filename('pyramid_frontend', 'static')


default_sentinel = object()


class Theme(object):
    """
    Represents a collection of templates, static files, image filters, and
    configuration corresponding to a particular visual theme (or "skin") used
    by the application.

    New themes are created by subclassing from this class. When passed to
    ``config.add_theme()``, The subclass will be instantiated with the
    application's ``settings`` dict and prepared for use.
    """
    template_dir = 'templates'
    static_dir = 'static'
    assets = {}
    image_filters = []
    includes = []

    cache_impl = None
    cache_args = None

    def __init__(self, settings):
        self.settings = settings
        self._compiled_asset_cache = {}

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.key)

    @classmethod
    def qualify_path(cls, path):
        theme_file = os.path.abspath(inspect.getfile(cls))
        return os.path.join(os.path.dirname(theme_file), path)

    @classmethod
    def traverse_attributes(cls, name, qualify_paths=False):
        assert len(cls.__bases__) == 1, \
            "multiple inheritance not allowed for themes"
        while cls != Theme:
            el = getattr(cls, name)
            if qualify_paths:
                el = cls.qualify_path(el)
            yield cls.key, el
            cls = cls.__bases__[0]

    @reify
    def template_dirs(self):
        dirs = []
        for key, dir in self.__class__.traverse_attributes(
                'template_dir', qualify_paths=True):
            dirs.append(dir)
        return dirs

    @reify
    def lookup(self):
        return self._make_lookup()

    @reify
    def lookup_nofilters(self):
        return self._make_lookup(clear_default_filters=True)

    def _make_lookup(self, clear_default_filters=False):
        default_filters = (['decode.utf8']
                           if clear_default_filters else
                           ['escape'])

        template_imports = [
            'from webhelpers2.html import escape',
        ]
        template_imports.extend(aslist(
            self.settings.get('pyramid_frontend.template_imports', ''),
            flatten=False))

        debug = asbool(self.settings.get('pyramid_frontend.debug'))
        base_module_dir = \
            self.settings.get('pyramid_frontend.module_directory')
        module_dir = base_module_dir and os.path.join(base_module_dir,
                                                      self.key)

        return SuperTemplateLookup(directories=self.template_dirs,
                                   input_encoding='utf-8',
                                   output_encoding='utf-8',
                                   imports=template_imports,
                                   default_filters=default_filters,
                                   filesystem_checks=debug,
                                   module_directory=module_dir,
                                   cache_impl=self.cache_impl,
                                   cache_args=self.cache_args)

    @reify
    def stacked_image_filters(self):
        filters = {}
        collected = self.__class__.traverse_attributes('image_filters')
        for key, class_list in reversed(list(collected)):
            class_dict = {chain.suffix: chain for chain in class_list}
            filters.update(class_dict)
        return filters.values()

    @reify
    def stacked_assets(self):
        asset_specs = {}
        collected = self.__class__.traverse_attributes('assets')
        for key, class_dict in reversed(list(collected)):
            asset_specs.update(class_dict)
        return asset_specs

    @reify
    def stacked_includes(self):
        includes = []
        collected = self.__class__.traverse_attributes('includes')
        for key, these in reversed(list(collected)):
            includes.extend(these)
        return includes

    @reify
    def keyed_static_dirs(self):
        cls = self.__class__
        stack = list(cls.traverse_attributes('static_dir', qualify_paths=True))
        stack.append(('pfe', static_dir))
        return stack

    def compiled_asset_path(self, key):
        if key in self._compiled_asset_cache:
            return self._compiled_asset_cache[key]
        else:
            map_path = os.path.join(
                self.settings['pyramid_frontend.compiled_asset_dir'],
                self.key,
                '%s.map' % key)
            with open(map_path) as f:
                self._compiled_asset_cache[key] = compiled_path = f.read()
                return compiled_path

    def static_url_to_filesystem_path(self, url):
        """
        Given a URL of the structure /_<theme key>/<path>, locate the static
        dir which corresponds to the theme key and re-qualify the <path> to
        that directory.
        """
        assert url.startswith('/_')
        theme_key, path = url[2:].split('/', 1)
        theme_dirs = dict(self.keyed_static_dirs)
        base_dir = theme_dirs[theme_key]
        return os.path.join(base_dir, path)

    def opt(self, key, default=default_sentinel):
        if default is default_sentinel:
            return getattr(self, key)
        else:
            return getattr(self, key, default)

    def static(self, path):
        for key, static_dir in self.keyed_static_dirs:
            if os.path.exists(os.path.join(static_dir, path)):
                return '/_%s/%s' % (key, path)
        raise IOError('path %r does not exist in any static dirs' % path)

    def compile(self, minify=True):
        output_dir = os.path.join(
            self.settings['pyramid_frontend.compiled_asset_dir'],
            self.key)
        for key, asset in self.stacked_assets.items():
            asset.compile(key=key,
                          theme=self,
                          output_dir=output_dir,
                          minify=minify)


def add_theme(config, cls):
    """
    A Pyramid config directive to initialiaze and register a theme for use.
    """
    resolved_cls = config.maybe_dotted(cls)

    settings = config.registry.settings
    theme = resolved_cls(settings)

    # Call includes
    package = inspect.getmodule(resolved_cls)
    resolver = DottedNameResolver(package=package)
    for include in theme.stacked_includes:
        config.include(resolver.maybe_resolve(include))

    # Register static dirs.
    static_dirs = settings.setdefault('pyramid_frontend.static_registry',
                                      set())
    for key, dir in theme.keyed_static_dirs:
        if (key, dir) not in static_dirs:
            static_dirs.add((key, dir))
            config.add_static_view('_%s' % key, path=dir)

    # Update global image filter registry as well, and ensure there are no
    # conflicts.
    for chain in theme.stacked_image_filters:
        config.add_image_filter(chain, with_theme=theme)

    def register(theme):
        themes = settings.setdefault('pyramid_frontend.theme_registry', {})
        themes[theme.key] = theme

    intr = config.introspectable(category_name='themes',
                                 discriminator=theme.key,
                                 title=theme.key,
                                 type_name=None)
    intr['theme'] = theme

    config.action(('theme', theme.key),
                  register,
                  args=(theme,),
                  introspectables=(intr,))


def set_theme_strategy(config, strategy_func):
    """
    A Pyramid config directive to set a customized theme-selection strategy for
    each request.
    """
    def register():
        registry = config.registry
        registry.pfe_theme_strategy = strategy_func

    config.action(('theme_strategy',), register)


def default_theme_strategy(request):
    """
    The default theme selection strategy: just checks the
    ``pyramid_frontend.theme`` settings key.
    """
    settings = request.registry.settings
    return settings['pyramid_frontend.theme']


def theme(request):
    """
    The theme instance that should be used for this request. This property is
    both lazily-evaluated and reified.
    """
    registry = request.registry
    strategy = getattr(registry, 'pfe_theme_strategy', default_theme_strategy)
    key = strategy(request)
    settings = registry.settings
    themes = settings.setdefault('pyramid_frontend.theme_registry', {})
    return themes[key]


def includeme(config):
    config.include('.images')
    config.include('.assets')

    config.add_directive('add_theme', add_theme)
    config.add_directive('set_theme_strategy', set_theme_strategy)

    config.add_request_method(theme, 'theme', reify=True)

    config.add_renderer(name='.html', factory=mako_renderer_factory)
    config.add_renderer(name='.txt', factory=mako_renderer_factory_nofilters)
