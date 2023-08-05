from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='appeus.theme',
      version=version,
      description="Installable theme: appeus.theme",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Mikel Larreategi',
      author_email='mlarreategi@codesyntax.com',
      url='https://bitbucket.org/codesyntax/appeus.theme/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['appeus'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plonetheme.bootstrap',
          'z3c.jbot',
          'five.grok',
          'plone.app.contenttypes',
          'cs.folderishpage',
          'appeus.content',
          'eea.tags',
          'eea.facetednavigation',
          'cs.editabletagline',
          'cs.editablefooter',
          'Products.PloneFormGen',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
