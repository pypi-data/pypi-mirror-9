from __future__ import absolute_import
from __future__ import division
import simplejson
from clint.textui import colored, puts, columns

from loveseat.suite import Suite


class TestRunner:
    def __init__(self, suitefile):
        with open(suitefile, 'r') as f:
            content = simplejson.loads(f.read())

        self.suite = Suite(
            content['suite'],
            content['slug'],
            content['tests'],
        )

    def run(self):
        results = self.suite.run()

        puts(colored.blue(self.suite.name))
        col = 30
        for result in results:
            puts(colored.magenta(result.name))
            puts(columns([(colored.green("Iterations")), col],
                         [(colored.green("{}".format(result.result_count))), col]))
            puts(columns([(colored.green("Average")), col],
                         [(colored.green("{} ms".format(result.result_avg / 1000))), col]))
            puts(columns([(colored.green("Max")), col],
                         [(colored.green("{} ms".format(result.result_max / 1000))), col]))
            puts(columns([(colored.green("Min")), col],
                         [(colored.green("{} ms".format(result.result_min / 1000))), col]))
            puts('\n')
