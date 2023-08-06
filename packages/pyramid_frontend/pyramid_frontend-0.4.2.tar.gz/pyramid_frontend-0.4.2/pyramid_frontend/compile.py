from __future__ import absolute_import, print_function, division

import logging

import argparse
import sys

from pyramid.paster import bootstrap


def compile(registry, minify=True):
    """
    Compile static assets for all themes which are registered in ``registry``.
    """
    log = logging.getLogger('pyramid_frontend')
    settings = registry.settings
    theme_registry = settings['pyramid_frontend.theme_registry']
    themes = theme_registry.values()
    count = len(themes)
    for ii, theme in enumerate(themes):
        log.warn("%d / %d - Compiling theme: %s", ii + 1, count, theme.key)
        theme.compile(minify=minify)


class ConsoleHandler(logging.StreamHandler):
    """
    A subclass of StreamHandler which behaves in the same way, but colorizes
    the log level before formatting it.
    """

    colors = {'CRITICAL': '[1;31m',
              'ERROR':    '[1;31m',
              'WARNING':  '[1;33m',
              'INFO':     '[1;32m',
              'DEBUG':    '[1;37m',
              None:    '[0m'}

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record, but
        before the formatter is applied the loglevel is colored.
        """

        record.colored_levelname = (self.colors[record.levelname] +
                                    record.levelname +
                                    self.colors[None])
        sys.stdout.write(self.format(record) + '\n')


def configure_logging(verbosity):
    """
    Configure logging for use with the asset compilation command.
    """
    levels = [logging.CRITICAL,
              logging.ERROR,
              logging.WARNING,
              logging.INFO,
              logging.DEBUG]

    ch = ConsoleHandler()
    ch.setLevel(levels[verbosity])

    formatter = logging.Formatter(
        '%(asctime)s %(colored_levelname)s %(name)s - %(message)s')
    ch.setFormatter(formatter)

    log = logging.getLogger('pyramid_frontend')
    log.setLevel(logging.DEBUG)
    log.addHandler(ch)
    return log


def main(args=sys.argv):
    """
    Main entry point for the executable which compiles assets.
    """
    parser = argparse.ArgumentParser(description='Compile static assets.')
    parser.add_argument('--no-minify', action='store_true', default=False)
    parser.add_argument('-v', '--verbose', action='count', default=2)
    parser.add_argument('config_uri')

    options = parser.parse_args(args[1:])

    env = bootstrap(options.config_uri)
    configure_logging(options.verbose)
    registry = env['registry']
    compile(registry, minify=(not options.no_minify))
    return 0
