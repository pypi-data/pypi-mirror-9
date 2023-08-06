from __future__ import absolute_import
import requests
from loveseat.result import Result


def read(database, id, **kwargs):
    params = kwargs.get('params', {})
    resp = requests.get(database,
                        params=params,
                        headers=kwargs.get('headers', {}))
    return Result(
        database=(kwargs.get('slug') or database),
        params=params,
        elapsed=resp.elapsed,
        test='read'
    )


def all_docs(database, **kwargs):
    params = kwargs.get('params', {})
    resp = requests.get("{database}/_all_docs".format(database=database),
                        params=params,
                        headers=kwargs.get('headers', {}))
    return Result(
        database=(kwargs.get('slug') or database),
        params=params,
        elapsed=resp.elapsed,
        test='all_docs'
    )


def view(database, view, **kwargs):
    params = kwargs.get('params', {})
    resp = requests.get("{database}/{view}".format(database=database, view=view),
                        params=params,
                        headers=kwargs.get('headers', {}))
    return Result(
        database=(kwargs.get('slug') or database),
        params=params,
        elapsed=resp.elapsed,
        test='view'
    )
