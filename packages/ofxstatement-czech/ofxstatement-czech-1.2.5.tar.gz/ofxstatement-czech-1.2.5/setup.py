#!/usr/bin/python3
"""Setup
"""
from setuptools import find_packages
from distutils.core import setup

version = "1.2.5"

with open('README.rst') as f:
    long_description = f.read()

setup(name='ofxstatement-czech',
      version=version,
      author="Matěj Cepl",
      author_email="mcepl@cepl.eu",
      url="https://gitlab.com/mcepl/ofxstatement-czech",
      description=("Czech banks plugin for ofxstatement"),
      long_description=long_description,
      license="GPLv3",
      keywords=["ofx", "ofxstatement"],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU Affero General Public License v3'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=["ofxstatement", "ofxstatement.plugins"],
      entry_points={
          'ofxstatement':
          ['gpc = ofxstatement.plugins.gpc:GPCPlugin',
           'maxibps = ofxstatement.plugins.maxibps:PSPlugin']
      },
      install_requires=['ofxstatement'],
      test_suite="src.ofxstatement.plugins.tests",
      include_package_data=True,
      zip_safe=True
      )
