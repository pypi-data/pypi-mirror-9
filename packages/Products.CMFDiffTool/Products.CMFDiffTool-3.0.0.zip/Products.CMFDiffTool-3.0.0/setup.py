# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '3.0.0'

setup(name='Products.CMFDiffTool',
      version=version,
      description="Diff tool for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.7",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Topic :: Internet :: WWW/HTTP",
        ],
      keywords='Diff Plone',
      author='Brent Hendricks',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/Products.CMFDiffTool',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.component',
            'plone.app.testing',
            'plone.namedfile',
            'plone.app.dexterity',
            'plone.app.contenttypes',
        ]
      ),
      install_requires=[
        'setuptools',
        'zope.interface',
        'Products.CMFCore',
        'Products.GenericSetup',
        'Acquisition',
        'Zope2',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
