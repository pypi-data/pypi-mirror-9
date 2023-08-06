from __future__ import absolute_import
from __future__ import division
import simplejson
from clint import textui

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

        textui.puts(textui.colored.blue(self.suite.name))

        for ag_result in results:
            column_results = ag_result.results
            column_width = 30

            output = [[textui.colored.magenta(ag_result.name), column_width]]
            output += map(lambda db: [textui.colored.magenta(db.split('/')[-1]), column_width],
                          column_results.keys())

            textui.puts(textui.columns(*output))

            metrics = ['count', 'avg', 'max', 'min']

            for m in metrics:
                output = [[m, column_width]]
                for r in column_results.items():
                    if m != 'count':
                        formatted = "{} ms".format(r[1][m] / 1000)
                    else:
                        formatted = unicode(r[1][m])
                    output.append([formatted, column_width])

                textui.puts(textui.columns(*output))

            textui.puts('\n')
