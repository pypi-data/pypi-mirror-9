from __future__ import absolute_import
from loveseat.couch_test import CouchTest
from loveseat.couch_specs import CouchReadSpec, CouchAllDocsSpec, CouchViewSpec


class Suite:
    def __init__(self, name, slug, tests):
        self.name = name
        self.slug = slug

        self.tests = []

        for test in tests:
            if test['test'] == 'read':
                self.tests.append(CouchTest(test['test'], spec=CouchReadSpec(test)))
            elif test['test'] == 'all_docs':
                self.tests.append(CouchTest(test['test'], spec=CouchAllDocsSpec(test)))
            elif test['test'] == 'view':
                self.tests.append(CouchTest(test['test'], spec=CouchViewSpec(test)))

    def run(self):
        results = []

        for test in self.tests:
            results.append(test.run())

        return results
