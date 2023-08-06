from __future__ import absolute_import
import jsonobject as jo
from loveseat.couch_runners import read, all_docs, view


class CouchDatabaseSpec(jo.JsonObject):
    url = jo.StringProperty(required=True)
    slug = jo.StringProperty()
    params = jo.base.DefaultProperty()
    headers = jo.base.DefaultProperty()


class CouchSpec(jo.JsonObject):
    name = jo.StringProperty(required=True)
    test = jo.StringProperty(required=True)
    databases = jo.ListProperty(CouchDatabaseSpec)
    repeat = jo.IntegerProperty(default=10)
    params = jo.base.DefaultProperty()
    headers = jo.base.DefaultProperty()

    def __init__(self, obj=None, **kwargs):
        database_specs = []
        databases = (obj or kwargs).get('databases')

        for database in databases:
            spec = {
                'params': (obj or kwargs).get('params', {}),
                'headers': (obj or kwargs).get('headers', {})
            }
            if isinstance(database, unicode) or isinstance(database, str):
                spec.update({'url': database, 'slug': database})
                database_specs.append(spec)
            else:
                spec.update(database)
                if 'slug' not in spec:
                    spec['slug'] = spec['url']
                database_specs.append(spec)

        (obj or kwargs)['databases'] = database_specs

        super(CouchSpec, self).__init__(obj, **kwargs)


class CouchReadSpec(CouchSpec):

    ids = jo.ListProperty(required=True)

    def __call__(self):
        for db in self.databases:
            yield read(db.url, self.ids, params=self.params, headers=self.headers, slug=db.slug)


class CouchAllDocsSpec(CouchSpec):

    def __call__(self):
        for db in self.databases:
            yield all_docs(db.url, params=self.params, slug=db.slug)


class CouchViewSpec(CouchSpec):
    view = jo.StringProperty(required=True)

    def __call__(self):
        for db in self.databases:
            yield view(db.url, self.view, params=self.params, headers=self.headers, slug=db.slug)
