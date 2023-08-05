#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

name = 'seantis.translators'
description = (
    'A directory of translators working for Zug PD.'
)
version = '0.3'

requirements = [
    'Plone>=4.3',
    'plone.api',
    'plone.app.dexterity [grok]',
    'five.grok',
    'seantis.plonetools',
    'seantis.people>=0.21'
]

test_requirements = [
    'plone.app.testing',
    'collective.betterbrowser[pyquery]',
    'seantis.plonetools[tests]',
    'mock'
]


def get_long_description():
    readme = open('README.rst').read()
    history = open(os.path.join('docs', 'HISTORY.rst')).read()

    # cut the part before the description to avoid repetition on pypi
    readme = readme[readme.index(description) + len(description):]

    return '\n'.join((readme, history))

setup(
    name=name, version=version, description=description,
    long_description=get_long_description(),
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='seantis.translators plone',
    author='Seantis GmbH',
    author_email='Seantis GmbH',
    url='https://github.com/seantis/seantis.translators',
    license='GPLv2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages='seantis.translators'.split('.')[:-1],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements,
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """
)
