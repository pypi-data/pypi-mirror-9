from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='pypostalcode',
      version=version,
      description="Radius searches on Canadian postal codes, location data",
      long_description=open("README.txt").read() + '\n\n',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Canada postal code code distance',
      author='Scott Rodkey',
      author_email='rodkeyscott@gmail.com',
      url='https://github.com/inkjet/pypostalcode',
      download_url='https://github.com/inkjet/pypostalcode/tarball/0.3',	
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'pysqlite'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
