Advanced Usage
==============


Theme Inheritance
-----------------

Themes can stack on top of another theme by subclassing them.


Templates
~~~~~~~~~

An inheriting theme's templates will layer on top of the superclass theme's
templates. The renderer will attempt to resolve templates to the child-most
class first, then traverse up the inheritance chain.

Inside a template, you can refer to files with the prefix ``super:`` to make
the filename resolve in the theme that is being inherited from.

Image Filters
~~~~~~~~~~~~~

An inheriting theme's image filters will layer on top of the superclass theme's
image filters. If an image filter of the same name is specified, the child
class will override the superclass.

Assets
~~~~~~

An inheriting theme's asset entry points will layer on top of the super class
theme's entry points. If an entry point of the same name is specified, the
child class will override the superclass.

Static Files
------------

Each theme has exactly one static file directory. It will be served up at an
underscore-prefixed path corresponding to the theme's key.


Asset Compilation
-----------------

The ``assets`` dict attribute maps entry point names to a tuple of URL paths
and asset type.

In development, simply call ``request.asset_tag(key)`` to generate an asset tag.

In production, assets must be compiled before that call. The asset compilation
step does the following for each entry point in each theme:

- Resolve the entry point path to a filesystem path.
- Collect static dirs from the theme and superclasses for use in resolving
  references during the compilation process.
- Compile the asset by calling a ``Compiler`` instance with the theme and the
  asset entry point.
- Save the result to a file in ``pyramid_frontend.compiled_asset_dir`` with a
  filename based on the sha1 of the contents.  - Collect all filenames for
  compiled files, mapping entry point name to filename.
- Write the filename to a file with a path like
  ``<compiled asset dir>/<theme key>/<entry point>.map``.

For normal usage, you can compile assets simply with::

    $ pcompile production.ini

Other options which can be useful are::

    $ pcompile --no-minify production.ini

Print debugging output::

    $ pcompile -vv production.ini

It's also possible to programmatically call the asset compilation step (for example, for embedding in other deployment tools), with the ``compile()`` function.


.. autofunction:: pyramid_frontend.compile.compile
    :noindex:
