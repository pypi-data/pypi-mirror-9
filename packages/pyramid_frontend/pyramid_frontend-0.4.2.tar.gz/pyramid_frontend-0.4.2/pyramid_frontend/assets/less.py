from __future__ import absolute_import, print_function, division

import os
import re
import io

from webhelpers2.html.tags import HTML

import six

from .asset import Asset


class LessAsset(Asset):
    """
    Asset handler for LESS CSS files. In production, autoprefixer is used.
    """
    extension = 'css'

    import_re = re.compile(r'@import[ ]+"(?P<path>.*)";')

    def __init__(self, url_path,
                 less_path='/_pfe/less.js',
                 lessc_path='lessc',
                 autoprefixer_path='autoprefixer'):
        self.url_path = url_path
        self.less_path = less_path
        self.lessc_path = lessc_path
        self.autoprefixer_path = autoprefixer_path

    def compile(self, key, theme, output_dir, minify=True):
        """
        Compile a LESS entry point.
        """
        entry_point = theme.static_url_to_filesystem_path(self.url_path)

        lessc_flags = [self.lessc_path]
        lessc_flags.append('--verbose')
        if minify:
            lessc_flags.append('--compress')

        preprocessed = self.concatenate(theme, entry_point)
        assert isinstance(preprocessed, six.text_type)

        preprocessed = preprocessed.encode('utf-8')

        with self.tempfile() as (in_f, in_name):
            in_f.write(preprocessed)
            in_f.flush()
            lessc_cmd = lessc_flags + [in_name]
            with self.tempfile() as (out_f, out_name):

                lessc_cmd.append(out_name)
                self.run_command(lessc_cmd)

                autoprefixer_cmd = [self.autoprefixer_path, out_name]
                self.run_command(autoprefixer_cmd)

                file_path = self.write_from_file(key, out_name, entry_point,
                                                 output_dir)

        return file_path

    def concatenate(self, theme, start_path):
        """
        Combine a LESS file and its `@import`s, recursively. Used to keep
        the ``lessc`` command-line compiler from having to traverse a directory
        structure, which it doesn't support very well right now.

        Always assumes file encodings are UTF-8, and should always return a
        unicode string (unicode on 2.x, str on 3.x).
        """
        err = 'File does not exist {0}'.format(start_path)
        assert os.path.isfile(start_path), err
        contents = []
        directory = os.path.dirname(start_path)
        with io.open(start_path, encoding='utf8') as fp:
            for line in fp:
                match = self.import_re.match(line.strip())
                if match:
                    path = match.groupdict()['path']
                    ext = os.path.splitext(path)[1]
                    if ext not in ('.css', '.less'):
                        path = '.'.join((path, 'less'))
                    if os.path.isabs(path):
                        path = theme.static_url_to_filesystem_path(path)
                    else:
                        path = os.path.join(directory, path)
                    contents.append(self.concatenate(theme, path))
                else:
                    contents.append(line)
        return u''.join(contents)

    def tag_development(self, theme, url):
        """
        Return an HTML fragment to use a less CSS entry point in development.
        """
        return ''.join([
            HTML.link(rel='stylesheet/less', type='text/css', href=url),
            HTML.script(src=self.less_path),
        ])

    def tag_production(self, theme, url):
        """
        Return an HTML fragment to use a less CSS entry point in production.
        """
        return HTML.link(rel='stylesheet', type='text/css', href=url)
