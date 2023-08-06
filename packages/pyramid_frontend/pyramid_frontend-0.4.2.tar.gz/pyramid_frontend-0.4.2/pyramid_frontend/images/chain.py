from __future__ import absolute_import, print_function, division

import os
import stat

from shutil import copyfileobj

from .files import filter_sep
from .filters import (PNGSaver, PNGProcessor, JPGSaver, JPGProcessor,
                      ThumbFilter)

savers = {
    'png': PNGSaver,
    'jpg': JPGSaver,
}


postprocessors = {
    'png': PNGProcessor,
    'jpg': JPGProcessor,
}


class FilterChain(object):
    """
    A chain of image filters (a.k.a. "pipeline") used to process images for a
    particular display context.
    """
    def __init__(self, suffix, filters=(), extension='png',
                 width=None, height=None, no_thumb=False,
                 pad=False, crop=False, crop_whitespace=False,
                 background='white', enlarge=False,
                 **saver_kwargs):

        self.suffix = suffix
        self.filters = list(filters)
        self.width = width
        self.height = height
        self.extension = extension

        assert filter_sep not in suffix, \
            "filter suffix cannot contain %r" % filter_sep
        assert suffix.lower() == suffix, \
            "filter suffix must be lowercase"

        if not no_thumb:
            self.filters.append(ThumbFilter(
                (width, height),
                pad=pad, crop=crop, crop_whitespace=crop_whitespace,
                background=background, enlarge=enlarge))

        saver_class = savers[self.extension]
        self.filters.append(saver_class(**saver_kwargs))

        self.filters.append(postprocessors[self.extension]())

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.suffix)

    def basename(self, name, original_ext):
        return ''.join([name,
                        filter_sep,
                        original_ext,
                        filter_sep,
                        self.suffix,
                        '.',
                        self.extension])

    def run_chain(self, image_data):
        for filter in self.filters:
            image_data = filter(image_data)
        return image_data

    def write(self, dest_path, filtered):
        # We have the final image data, now save it.
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        copyfileobj(filtered, open(dest_path, 'wb'))

        # Make this writable by everyone.
        bits = os.stat(dest_path).st_mode
        os.chmod(dest_path, bits | stat.S_IWGRP | stat.S_IWOTH)

        return True

    def run(self, dest_path, image_data):
        filtered = self.run_chain(image_data)
        return self.write(dest_path, filtered)


class PassThroughFilterChain(FilterChain):
    """
    A filter chain which does not do any manipulation, only applies lossless
    optimization tools.
    """
    def __init__(self, suffix=None, filters=()):
        self.suffix = suffix
        self.extension = None
        self.filters = filters
        self.width = None
        self.height = None

    def basename(self, name, original_ext):
        return '%s.%s' % (name, original_ext)

    def run(self, dest_path, image_data):
        filtered = self.run_chain(image_data)
        ext = dest_path.rsplit('.', 1)[-1]
        if ext in postprocessors:
            filtered = postprocessors[ext]()(filtered)
        return self.write(dest_path, filtered)
