from __future__ import absolute_import, print_function, division

from webhelpers2.html.tags import HTML

from .asset import Asset


class SVGAsset(Asset):
    """
    Asset handler for SVG files.
    """
    extension = 'svg'

    def compile(self, key, theme, output_dir, minify=True):
        """
        Compile an SVG entry point.
        """
        entry_point = theme.static_url_to_filesystem_path(self.url_path)
        file_path = self.write_from_file(key, entry_point, self.url_path,
                                         output_dir)
        return file_path

    def tag(self, theme, url, **kw):
        return HTML.img(src=url, alt=kw.get('alt', ''), **kw)
