from __future__ import absolute_import

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#import loveseat

setup(
    name='loveseat',
    version='0.0.2c',
    description='Benchmark library for testing CouchDB',
    author='Dimagi',
    author_email='dev@dimagi.com',
    url='http://github.com/dimagi/loveseat',
    license='MIT',
    entry_points={
        'console_scripts': [
            'loveseat = loveseat.__main__:main'
        ]
    },
    install_requires=[
        'requests',
        'clint',
        'jsonobject',
        'simplejson',
    ],
)
