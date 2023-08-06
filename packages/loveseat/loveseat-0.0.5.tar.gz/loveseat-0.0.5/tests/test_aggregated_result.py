from __future__ import absolute_import
import unittest
from datetime import timedelta
from loveseat.aggregated_result import AggregatedResult
from loveseat.result import Result


class TestAggregatedResult(unittest.TestCase):

    def setUp(self):
        self.resultOne = Result(database='a', elapsed=timedelta(0, 0, 2))
        self.resultTwo = Result(database='a', elapsed=timedelta(0, 0, 4))
        self.resultThree = Result(database='b', elapsed=timedelta(0, 0, 5))

    def test_aggregated_result(self):
        ag = AggregatedResult('example')

        ag.add_results([self.resultOne, self.resultTwo, self.resultThree])
        self.assertEqual(ag.results['a']['avg'], 3)
        self.assertEqual(ag.results['a']['max'], 4)
        self.assertEqual(ag.results['a']['min'], 2)
        self.assertEqual(ag.results['a']['count'], 2)

        self.assertEqual(ag.results['b']['avg'], 5)
        self.assertEqual(ag.results['b']['max'], 5)
        self.assertEqual(ag.results['b']['min'], 5)
        self.assertEqual(ag.results['b']['count'], 1)
