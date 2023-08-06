from collections import defaultdict


class AggregatedResult(object):
    """
    Keeps track of various statistics for Result objects. It separates statistics
    based on database name.
    """
    def __init__(self, name):
        self.name = name
        self.results = defaultdict(lambda: {
            'count': 0,
            'avg': None,
            'min': None,
            'max': None,
        })

    def add_result(self, result):
        entry = self.results[result.database]

        microseconds = result.elapsed.microseconds
        entry['avg'] = ((entry['avg'] or 0) * entry['count'] + microseconds) \
            / (entry['count'] + 1)

        entry['count'] += 1
        if microseconds > entry['max']:
            entry['max'] = microseconds
        if microseconds < entry['min'] or not entry['min']:
            entry['min'] = microseconds

    def add_results(self, results):
        for result in results:
            self.add_result(result)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()
