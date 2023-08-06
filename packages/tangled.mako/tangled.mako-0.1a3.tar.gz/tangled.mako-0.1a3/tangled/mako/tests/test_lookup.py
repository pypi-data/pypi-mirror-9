import unittest

from tangled.mako import create_lookup
from tangled.util import abs_path


class Tests(unittest.TestCase):

    def test_lookup(self):
        settings = {
            'mako.lookup.directories': 'tangled.mako.tests:templates',
        }
        lookup = create_lookup(settings)
        lookup.get_template('test.mako')

    def test_lookup_asset_path(self):
        lookup = create_lookup({})
        lookup.get_template('tangled.mako.tests:templates/test.mako')

    def test_lookup_abs_path(self):
        lookup = create_lookup({})
        lookup.get_template(abs_path('tangled.mako.tests:templates/test.mako'))
