#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import simple_elasticsearch

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'elasticsearch>=1.0.0,<2.0.0',
    'elasticsearch-dsl>=0.0.2'
]

test_requirements = [
    'datadiff>=1.1.6',
    'mock>=1.0.1'
]

setup(
    name='django-simple-elasticsearch',
    version=simple_elasticsearch.__version__,
    description='Simple ElasticSearch indexing integration for Django.',
    long_description=readme + '\n\n' + history,
    author='James Addison',
    author_email='code@scottisheyes.com',
    url='https://github.com/jaddison/django-simple-elasticsearch',
    packages=[
        'simple_elasticsearch',
        'simple_elasticsearch.management',
        'simple_elasticsearch.management.commands',
    ],
    package_dir={'django-simple-elasticsearch':
                 'django-simple-elasticsearch'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='django simple elasticsearch search indexing haystack',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='runtests.runtests',
    tests_require=test_requirements
)
