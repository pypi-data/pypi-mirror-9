# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '3.0.3'

setup(
    name='plone.app.content',
    version=version,
    description="Content Views for Plone",
    long_description='\n\n'.join([
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ]),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='plone content views viewlet',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='http://pypi.python.org/pypi/plone.app.content',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'plone.app.testing',
            'plone.app.contenttypes',
        ]
    ),
    install_requires=[
        'Acquisition',
        'Products.CMFCore>=2.2.0dev',
        'Products.CMFDefault',
        'Products.CMFDynamicViewFTI',  # required for cmf.ModifyViewTemplate
        'Products.CMFPlone',
        'Zope2',
        'plone.app.widgets>=2.0.0.dev0',
        'plone.batching',
        'plone.i18n',
        'plone.memoize',
        'setuptools',
        'zope.component',
        'zope.container',
        'zope.event',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        'zope.viewlet',
    ],
)
