from __future__ import absolute_import, print_function, division

import os.path
import mimetypes
import pkg_resources

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.static import FileResponse
from pyramid.settings import asbool
from lockfile import FileLock

from .files import filter_sep, prefix_for_name, processed_path, original_path


plausible_extensions = set([
    'jpg',
    'jpeg',
    'gif',
    'png',
    'tif',
    'tiff',
    'ppm',
    'bmp',
    'tga',
])


def get_image_filter(registry, filter_key):
    filter_registry = getattr(registry, 'image_filter_registry', {})
    chain, with_theme = filter_registry[filter_key]
    return chain


class MissingOriginal(Exception):

    def __init__(self, path, chain):
        self.path = path
        self.chain = chain
        Exception.__init__(self, 'Missing file %s' % path)


def process_image(settings, name, original_ext, chain, overwrite=False):
    proc_path = processed_path(settings, name, original_ext, chain)
    if overwrite or (not os.path.exists(proc_path)):
        dest_dir = os.path.dirname(proc_path)
        try:
            os.makedirs(dest_dir)
        except OSError:
            pass

        lock = FileLock(proc_path + '.lock')
        with lock:
            if overwrite or (not os.path.exists(proc_path)):
                orig_path = original_path(settings, name, original_ext)
                if not os.path.exists(orig_path):
                    raise MissingOriginal(path=orig_path, chain=chain)
                image_data = open(orig_path, 'rb')
                chain.run(proc_path, image_data)
    return proc_path


class ImageView(object):

    def __init__(self, request):
        self.request = request

    def placeholder(self, chain):
        orig_path = pkg_resources.resource_filename('pyramid_frontend.images',
                                                    'no-image.png')
        image_data = open(orig_path, 'rb')
        f = chain.run_chain(image_data)

        response = Response(f.read())
        response.content_type = \
            mimetypes.guess_type('x.%s' % chain.extension)[0]

        return response

    def __call__(self):
        request = self.request
        settings = request.registry.settings

        url_prefix = self.request.matchdict['prefix']
        name = self.request.matchdict['name']
        name, ext = name.rsplit('.', 1)

        if filter_sep in name:
            parts = name.split(filter_sep, 2)
            if len(parts) == 3:
                name, original_ext, chain_name = parts
            else:
                raise HTTPNotFound()
        else:
            original_ext = ext
            chain_name = None

        try:
            chain = get_image_filter(request.registry, chain_name)
        except KeyError:
            raise HTTPNotFound()

        if ((chain.extension and chain.extension != ext) or
                prefix_for_name(name) != url_prefix):
            raise HTTPNotFound()

        if original_ext not in plausible_extensions:
            raise HTTPNotFound()

        debug = asbool(settings.get('pyramid_frontend.debug'))
        overwrite = debug and request.params.get('overwrite')

        try:
            proc_path = process_image(settings, name, original_ext, chain,
                                      overwrite=overwrite)
        except MissingOriginal:
            if debug:
                return self.placeholder(chain)
            else:
                raise
        return FileResponse(proc_path, self.request)
