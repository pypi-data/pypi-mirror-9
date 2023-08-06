from __future__ import absolute_import
import unittest
from datetime import timedelta
from loveseat.aggregated_result import AggregatedResult
from loveseat.result import Result


class TestAggregatedResult(unittest.TestCase):

    def setUp(self):
        self.resultOne = Result(elapsed=timedelta(0, 0, 2))
        self.resultTwo = Result(elapsed=timedelta(0, 0, 4))

    def test_aggregated_result(self):
        ag = AggregatedResult('example')

        ag.add_result(self.resultOne)
        self.assertEqual(ag.result_avg, 2)
        self.assertEqual(ag.result_min, 2)
        self.assertEqual(ag.result_max, 2)
        self.assertEqual(ag.result_count, 1)

        ag.add_result(self.resultTwo)
        self.assertEqual(ag.result_avg, 3)
        self.assertEqual(ag.result_min, 2)
        self.assertEqual(ag.result_max, 4)
        self.assertEqual(ag.result_count, 2)
