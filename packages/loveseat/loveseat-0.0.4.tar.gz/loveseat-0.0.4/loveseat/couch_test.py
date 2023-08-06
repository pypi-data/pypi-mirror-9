from __future__ import absolute_import
from loveseat.aggregated_result import AggregatedResult


class CouchTest(object):
    def __init__(self, test, spec=None):
        self.test = test
        self.spec = spec

    def agg_result(self):
        return AggregatedResult(self.spec.name)

    def run(self):
        iterations = self.spec.repeat
        agg_result = self.agg_result()

        while iterations:
            agg_result.add_results(list(self.spec()))
            iterations -= 1

        return agg_result
