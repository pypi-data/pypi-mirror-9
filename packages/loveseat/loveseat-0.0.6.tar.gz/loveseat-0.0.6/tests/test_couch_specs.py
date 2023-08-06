from __future__ import absolute_import
import unittest
from os.path import abspath, dirname, join
from loveseat.couch_specs import CouchReadSpec


class TestCouchSpecs(unittest.TestCase):
    def test_multiple_databases(self):
        db_url = 'http://localhost:5984/commcarehq'
        db_dict = {
            'url': 'my://broken/url',
            'params': {
                'my': 'param'
            }
        }
        spec = {
            'name': 'dummy',
            'test': 'read',
            'databases': ['http://localhost:5984/commcarehq', db_dict],
            'params': {},
            'repeat': 100,
            'headers': {
                'silly': 'header'
            },
            'ids': ['000382ba-386f-4757-a80b-8a8aa62eec97']
        }

        read_spec = CouchReadSpec(spec)

        self.assertEqual(len(read_spec.databases), 2)
        self.assertEqual(read_spec.databases[0]['url'], db_url)
        self.assertEqual(read_spec.databases[0]['headers']['silly'], 'header')

        self.assertEqual(read_spec.databases[1]['url'], db_dict['url'])
        self.assertEqual(read_spec.databases[1]['headers']['silly'], 'header')
        self.assertEqual(read_spec.databases[1]['params']['my'], 'param')
