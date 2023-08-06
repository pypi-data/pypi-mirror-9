try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='loveseat',
    version='0.0.1',
    description='Benchmark library for testing CouchDB',
    author='Dimagi',
    author_email='dev@dimagi.com',
    url='http://github.com/dimagi/loveseat',
    license='MIT',
    install_requires=[
        'requests',
        'jsonobject',
        'clint',
    ],
)
