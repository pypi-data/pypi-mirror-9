from __future__ import absolute_import
import unittest
from os.path import abspath, dirname, join
from loveseat.test_runner import TestRunner

THISDIR = dirname(abspath(__file__))
BASE_PATH = join(THISDIR, 'data')


class TestTestRunner(unittest.TestCase):
    def setUp(self):
        self.suitefile = join(BASE_PATH, 'test_suite.json')

    def test_init_test_runner(self):
        runner = TestRunner(self.suitefile)

        self.assertEqual(runner.suite.slug, 'example_suite')
        self.assertEqual(runner.suite.name, 'Example Suite')
        self.assertEqual(len(runner.suite.tests), 4)
