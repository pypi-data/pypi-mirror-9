# -*- coding: utf-8 -*-
"""Installer for the blog.policy package."""

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
    name='blog.policy',
    version='0.1b8',
    description="A policy for blog suite",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Plone Python Imio',
    author='bsuttor',
    author_email='ben.suttor@gmail.com',
    url='https://github.com/IMIO/blog.policy',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['blog'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'setuptools',
        'blog.post',
        'sc.social.like',
        'collective.quickupload',
        'collective.contentrules.yearmonth',
        'plonetheme.bootstrap',
        'plone.formwidget.captcha',
        'collective.atomrss',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.robotframework',
        ],
    },
    entry_points="""
    """,
)
