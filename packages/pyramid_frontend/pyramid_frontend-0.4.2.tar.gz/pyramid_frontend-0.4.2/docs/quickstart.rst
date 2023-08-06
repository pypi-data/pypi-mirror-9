Quick Start
===========


Install
-------

Install with pip::

    $ pip install pyramid_frontend


Integrate with a Pyramid App
----------------------------

Include pyramid_frontend, by calling ``config.include('pyramid_frontend')`` or
adding pyramid_frontend to ``pyramid.includes``.

Configure the following settings:

* ``pyramid_frontend.compiled_asset_dir``
* ``pyramid_frontend.original_image_dir``
* ``pyramid_frontend.processed_image_dir``

* ``pyramid_frontend.compile``


Add Themes
----------

Register at least one theme, using the ``config.add_theme(theme)`` directive.
You can also pass a dotted string (e.g. ``myapp.themes.foo.FooTheme``) which
will be resolved relative to the calling module.

Other possible mechanisms for theme registration which may be added later are a
setuptools entrypoint or a settings key.

* Themes are subclasses of the ``pyramid_frontend.Theme`` class.
* Class attributes or properties can be set for resource configuration.
* Paths are interpreted as relative to the directory of the module containing
  the class definition.
* An example:

.. code-block:: python

    class MyTheme(Theme):
        template_dir = ...
        static_dir = ...
        image_filters = {
            'detail': ...
            'thumb': ...
        }
        assets = {
            'main-js': ('static/js/main.js', 'requirejs'),
            'main-less': ('static/css/main.less', 'less'),
        }


Use a Theme
-----------

Configure your application to use a theme, with one of the following methods:

* Specify the ``pyramid_frontend.theme`` setting key.
* Call ``config.set_theme_strategy(func)`` with a function that will return the
  theme to use.
* An example:

.. code-block:: python

    def mobile_theme_strategy(request):
        if request.is_mobile and not request.session.get('use_desktop'):
            return 'my-mobile-theme'
        else:
            return 'my-desktop-theme'

Inside your app, specify a .html or .txt renderer. It will be rendered using
the currently active theme (or call the theme strategy function to determine
which theme to use).

The ``request`` object has a few added methods.

* ``request.asset_tag(key)`` - Generate an asset tag (either a script tag or
  stylesheet tag, or some combination thereof) for a corresponding asset key.
  In production, this will point to a concatenated / minified file.

* ``request.image_url(name, original_ext, filter_key)`` - Generate a URL for an
  image as processed by the specified filter chain.
* ``request.image_tag(name, original_ext, filter_key, **kwargs)`` - Generate an
  img tag for an image as processed by the specified filter chain.
* ``request.image_original_path(name, original_ext)`` - Return the filesystem
  path to the original file for this image.

* ``request.theme`` is a reified property on ``request`` - Return the theme
  instance that will be used to serve this request.


Compile Assets
--------------

When using in production, call ``pcompile production.ini`` to generate static
assets, or call ``pyramid_frontend.compile(registry.settings)``.
