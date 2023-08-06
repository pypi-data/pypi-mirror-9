#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

from setuptools import find_packages, setup

import med_djutils


with open('README.rst') as f:
    readme = f.read()

packages = find_packages()

classifiers = (
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    # the FSF refers to it as "Modified BSD License". Other names include
    # "New BSD", "revised BSD", "BSD-3", or "3-clause BSD"
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Framework :: Django',
)

setup(
    name="medularis-django-utils",
    version=med_djutils.__version__,
    description="Medularis's open source utilities for use in Django projects",
    long_description=readme,
    author='German Larrain',
    author_email='glarrain@users.noreply.github.com',
    url='https://github.com/medularis/medularis-django-utils',
    packages=packages,
    install_requires=['Django>=1.6'],
    license='3-clause BSD',  # TODO: verify name is correct
    zip_safe=False,
    classifiers=classifiers,

    tests_require=[
        'Django>=1.6',
        'mock>=1.0.1',
    ],
    test_suite='runtests.runtests',
)
