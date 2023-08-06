from __future__ import absolute_import, print_function, division

from ..base import BaseTheme
from pyramid_frontend.images.chain import FilterChain


class BarTheme(BaseTheme):
    key = 'bar'
    image_filters = [
        FilterChain('barthumb', width=300, height=100, crop=True),
    ]
    includes = [
        '..base.base_includeme',
    ]
