from __future__ import absolute_import

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import loveseat

setup(
    name='loveseat',
    version=loveseat.__version__,
    description='Benchmark library for testing CouchDB',
    author=loveseat.__author__,
    author_email='dev@dimagi.com',
    url='http://github.com/dimagi/loveseat',
    license=loveseat.__licence__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'loveseat = loveseat.__main__:main'
        ]
    },
    install_requires=[
        'requests',
        'ndg-httpsclient',
        'pyopenssl',
        'pyasn1'
        'clint',
        'jsonobject',
        'simplejson',
    ],
)
