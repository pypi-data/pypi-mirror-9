from __future__ import absolute_import
from loveseat.aggregated_result import AggregatedResult


class CouchTest(object):
    def __init__(self, test, spec=None):
        self.test = test
        self.spec = spec

    def agg_result(self):
        return AggregatedResult(u'{} {} tests on {}'.format(
            self.spec.repeat,
            self.test,
            self.spec.database)
        )

    def run(self):
        iterations = self.spec.repeat
        agg_result = self.agg_result()

        while iterations > 0:
            agg_result.add_result(self.spec())
            iterations -= 1

        return agg_result
