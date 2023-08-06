from __future__ import absolute_import
import jsonobject as jo
from loveseat.couch_runners import read, all_docs, view


class CouchSpec(jo.JsonObject):
    test = jo.StringProperty(required=True)
    database = jo.StringProperty(required=True)
    repeat = jo.IntegerProperty(default=10)
    params = jo.base.DefaultProperty()


class CouchReadSpec(CouchSpec):

    ids = jo.ListProperty(required=True)

    def __call__(self):
        return read(self.database, self.params, self.ids)


class CouchAllDocsSpec(CouchSpec):

    def __call__(self):
        return all_docs(self.database, self.params)


class CouchViewSpec(CouchSpec):
    view = jo.StringProperty(required=True)

    def __call__(self):
        return view(self.database, self.params, self.view)
