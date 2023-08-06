try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import loveseat

setup(
    name='loveseat',
    version=loveseat.__version__,
    description='Benchmark library for testing CouchDB',
    author=loveseat.__author__,
    author_email='dev@dimagi.com',
    url='http://github.com/dimagi/loveseat',
    license=loveseat.__licence__,
    entry_points={
        'console_scripts': [
            'loveseat = loveseat.__main__:main'
        ]
    },
    install_requires=[
        'requests',
        'clint',
        'jsonobject'
    ],
)
