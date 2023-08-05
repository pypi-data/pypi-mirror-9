# -*- coding: utf-8 -*-
"""Installer for the collective.geo.leaflet package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='collective.geo.leaflet',
    version='0.1b7',
    description="Add geo views for dexterity content with leaflet js library",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='leaflet collective.geo geo plone dexterity map',
    author='Benoît Suttor',
    author_email='benoit.suttor@imio.be',
    url='http://pypi.python.org/pypi/collective.geo.leaflet',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.geo'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'setuptools',
        'collective.geo.settings',
        'collective.geo.geographer',
        'collective.geo.mapwidget',
        'collective.geo.behaviour',
        'collective.js.leaflet',
        'collective.geo.contentlocations',
        'collective.geo.json',
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
