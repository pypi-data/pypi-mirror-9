from __future__ import absolute_import

from loveseat.test_runner import TestRunner


def main():
    from loveseat.cli import parser
    args = parser.parse_args()

    runner = TestRunner(args.suitefile)
    runner.run()
