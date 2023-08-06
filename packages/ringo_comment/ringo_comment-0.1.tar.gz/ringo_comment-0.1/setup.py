# coding=utf8
from setuptools import setup, find_packages
import sys, os


setup(name='ringo_comment',
      version='0.1',
      description="Comment extension for the Ringo framework",
      long_description="""""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ringo extension',
      author='Torsten Irländer',
      author_email='torsten.irlaender@googlemail.com',
      url='https://bitbucket.org/ti/ringo_comment',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'ringo'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [babel.extractors]
      tableconfig = ringo.lib.i18n:extract_i18n_tableconfig
      formconfig = formbar.i18n:extract_i18n_formconfig
      """,
      message_extractors = {'ringo_comment': [
            ('**.py', 'python', None),
            ('templates/**.html', 'mako', None),
            ('templates/**.mako', 'mako', None),
            ('**.xml', 'formconfig', None),
            ('**.json', 'tableconfig', None),
            ('static/**', 'ignore', None)]},
      )
