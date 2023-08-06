class AggregatedResult(object):
    def __init__(self, name):
        self.name = name
        self.result_count = 0
        self.result_avg = None
        self.result_max = None
        self.result_min = None

    def add_result(self, result):
        microseconds = result.elapsed.microseconds
        self.result_avg = ((self.result_avg or 0) * self.result_count + microseconds) \
            / (self.result_count + 1)

        self.result_count += 1
        if microseconds > self.result_max:
            self.result_max = microseconds
        if microseconds < self.result_min or not self.result_min:
            self.result_min = microseconds

    def add_results(self, results):
        for result in results:
            self.add_result(result)

    def __unicode__(self):
        return u"======\nName: {}\nRuns: {} | Average: {} | Max {} | Min {}\n======".format(
            self.name,
            self.result_count,
            self.result_avg,
            self.result_max,
            self.result_min
        )

    def __str__(self):
        return self.__unicode__()
