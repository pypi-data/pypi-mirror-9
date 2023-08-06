from __future__ import absolute_import, print_function, division

import os
import shutil
import hashlib

from datetime import datetime

from PIL import Image


filter_sep = '_'


def prefix_for_name(name):
    """
    Return the 4-char hash prefix to use for this image name (prevents having
    too many images in the same directory).
    """
    return hashlib.md5(name.encode('utf-8')).hexdigest()[:4]


def get_url_prefix(settings):
    return settings.get('pyramid_frontend.image_url_prefix', '/img').\
        rstrip('/')


def save_image(settings, name, original_ext, f):
    prefix = prefix_for_name(name)
    ensure_dirs(settings, prefix)
    save_locally(original_path(settings, name, original_ext), f)


def save_locally(path, f):
    diskf = open(path, 'wb')
    f.seek(0)
    shutil.copyfileobj(f, diskf)
    diskf.close()


def check(f):
    """
    Given a file object, check to see if the contents is a valid image. If so,
    return the file format. Otherwise, raise exceptions.
    """
    im = Image.open(f)
    # Raises exceptions if the file is broken in any way.
    im.verify()
    return (im.format, im.mode)


def save_to_error_dir(settings, name, f):
    """
    Save a questionable image (could not be verified by PIL) to a penalty box
    for investigation.
    """
    prefix = datetime.utcnow().strftime('%m-%d-%Y.%H:%M:%S')
    dirpath = os.path.join(settings['pyramid_frontend.error_dir'], prefix)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    filepath = os.path.join(dirpath, name)
    save_locally(filepath, f)


def ensure_dirs(settings, prefix):
    dirpath = os.path.join(settings['pyramid_frontend.original_image_dir'],
                           prefix)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def original_path(settings, name, original_ext):
    dir = settings['pyramid_frontend.original_image_dir']
    return os.path.join(dir,
                        prefix_for_name(name),
                        '%s.%s' % (name, original_ext))


def processed_path(settings, name, original_ext, chain):
    dir = settings['pyramid_frontend.processed_image_dir']
    return os.path.join(
        dir,
        prefix_for_name(name),
        chain.basename(name, original_ext))


def check_and_save_image(settings, name, f):
    """
    Save an image to the local ``pyramid_frontend`` image originals directory,
    using the supplied base name and file-like object.

    The extension is chosen and normalized based on file format, and returned.
    It will always be three characters.

    If the image is not valid (cannot be loaded as a PIL image), it is saved to
    the error directory, and the exception raised by PIL is re-raised.
    """
    try:
        im = Image.open(f)
        format = im.format
        size = im.size
    except IOError:
        save_to_error_dir(settings, name, f)
        raise

    possible_extensions = {
        'JPEG': 'jpg',
        'PNG': 'png',
        'TIFF': 'tif',
        'GIF': 'gif',
    }
    original_ext = possible_extensions[format]
    save_image(settings, name, original_ext, f)
    f.close()
    return dict(ext=original_ext, size=size)
