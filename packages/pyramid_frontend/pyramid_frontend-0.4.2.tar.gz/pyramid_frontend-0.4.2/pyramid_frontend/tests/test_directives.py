from __future__ import absolute_import, print_function, division

from unittest import TestCase

from pyramid import testing
from ..images.chain import FilterChain


class TestConfig(TestCase):
    settings = {
        'pyramid_frontend.compiled_asset_dir': '.'
    }

    def setUp(self):
        self.config = testing.setUp(settings=self.settings)
        self.config.include('pyramid_frontend')

    def tearDown(self):
        testing.tearDown()

    def test_directives_get_registered(self):
        self.assertTrue(hasattr(self.config, 'add_image_filter'))
        self.assertTrue(hasattr(self.config, 'add_theme'))

    def test_register_filter_chain_twice(self):
        chain = FilterChain('blah', width=200, height=200,
                            crop=True, extension='png')
        self.config.add_image_filter(chain, None)
        self.config.add_image_filter(chain, None)

    def test_register_conflicting_filters(self):
        chain = FilterChain('blah', width=200, height=200,
                            crop=True, extension='png')
        self.config.add_image_filter(chain, None)
        chain = FilterChain('blah', width=200, height=200,
                            crop=True, extension='jpg', quality=85)
        with self.assertRaises(ValueError):
            self.config.add_image_filter(chain, None)
