# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + \
    read('CHANGES.rst')

setup(
    name='blog.post',
    version='0.1b3',
    description="This package is use to create a Plone blog site",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='Plone Python',
    author='Benoît Suttor',
    author_email='ben.suttor@gmail.com',
    url='http://pypi.python.org/pypi/blog.post',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['blog'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone',
        'setuptools',
        'plone.app.discussion',
    ],
    extras_require={
        'test': [
            'plone.app.robotframework',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
