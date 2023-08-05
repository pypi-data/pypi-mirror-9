#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('CHANGELOG.rst') as f:
    changelog = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Eve-Elastic',
    version='0.2.6',
    description='Elasticsearch data layer for eve rest framework',
    long_description=readme + '\n\n' + changelog,
    license=license,
    author='Petr Jasek',
    author_email='petr.jasek@sourcefabric.org',
    url='https://github.com/petrjasek/eve-elastic',
    packages=['eve_elastic'],
    tests_require=['nose'],
    install_requires=[
        'elasticsearch>=1.2.0',
        'arrow>=0.4.2',
        'Eve>=0.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    test_suite='eve_elastic.test.test_elastic'
)
