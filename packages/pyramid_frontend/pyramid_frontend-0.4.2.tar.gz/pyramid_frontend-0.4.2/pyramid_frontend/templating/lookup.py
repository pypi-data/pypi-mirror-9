from __future__ import absolute_import, print_function, division

import re
import posixpath
import os.path

from mako.exceptions import TopLevelLookupException
from mako.lookup import TemplateLookup


class SuperTemplateLookup(TemplateLookup):
    """
    A subclass of ``mako.lookup.TemplateLookup`` which provides an extra bit of
    functionality for building template inheritance chains.

    For normal documented usage, behavior is the same as the normal
    ``TemplateLookup`` class. However, it is additional possible for a template
    to inherit from another template which has the same file path, by prefixing
    the URI with ``super:``. This inheritance style is not possible with the
    base ``TemplateLookup``.
    """
    super_delimiter = '::'

    def find_dir_for_path(self, filename):
        """
        Given a file path, return the template directory within the lookup's
        list of directories where it can be found.
        """
        for dir in self.directories:
            if os.path.commonprefix([filename, dir]) == dir:
                return dir
        raise ValueError("filename %r is not in any of this lookup's "
                         "directories" % filename)

    def find_dir_for_uri(self, uri, start_index=0):
        """
        Given a template URI, return the first directory in the lookup's list
        of directories where it can be found, starting at the ``start_index``
        directory in the list.
        """
        u = re.sub(r'^\/+', '', uri)
        for dir in self.directories[start_index:]:
            srcfile = posixpath.normpath(posixpath.join(dir, u))
            if os.path.isfile(srcfile):
                return dir, srcfile
        return None, None

    def get_template(self, uri):
        """
        Fetch a template from this lookup.

        If uri containers the ``super_delimiter``, expect it to join a 2-tuple
        of ``(uri, dir)``. The ``dir`` component refers to the specific
        directory within the lookup that the template should be fetched from.
        """
        try:
            if self.filesystem_checks:
                return self._check(uri, self._collection[uri])
            else:
                return self._collection[uri]

        except KeyError:

            if self.super_delimiter in uri:
                file_path, from_dir = uri.split(self.super_delimiter)
                u = re.sub(r'^\/+', '', file_path)
                srcfile = posixpath.normpath(posixpath.join(from_dir, u))
                return self._load(srcfile, uri)

            else:
                dir, srcfile = self.find_dir_for_uri(uri)
                if not dir:
                    raise TopLevelLookupException(
                        "Cant locate template for uri %r" % uri)
                return self._load(srcfile, uri)

    def adjust_uri(self, uri, relativeto):
        """
        Adjust the supplied URI given a specific source directory. If the uri
        begins with ``super:``, relativeize the URI such that it refers to the
        URI specified in the next-higher template directory in the chain.
        """
        if uri.startswith('super:'):
            uri = uri[6:]
            relative_templ = self.get_template(relativeto)
            from_dir = self.find_dir_for_path(relative_templ.filename)
            assert from_dir, "can't find what dir calling template is in"
            start_index = self.directories.index(from_dir) + 1
            relpath = os.path.relpath(relative_templ.filename, from_dir)

            next_dir, srcfile = self.find_dir_for_uri(relpath, start_index)
            assert next_dir
        else:
            next_dir = None

        if self.super_delimiter in relativeto:
            relativeto = relativeto.split(self.super_delimiter)[0]

        uri = TemplateLookup.adjust_uri(self, uri, relativeto)
        if next_dir:
            assert self.super_delimiter not in uri
            new_uri = uri + self.super_delimiter + next_dir
            return new_uri
        else:
            return uri

    def filename_to_uri(self, filename):
        """
        Given a filename, return a URI which can be used to access this
        template from the lookup.
        """
        from_dir = self.find_dir_for_path(filename)
        base_uri = TemplateLookup.filename_to_uri(self, filename)
        ret = base_uri + self.super_delimiter + from_dir
        return ret
