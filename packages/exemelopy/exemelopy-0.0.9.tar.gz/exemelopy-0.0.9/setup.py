import os
from setuptools import setup, find_packages

execfile('exemelopy/__version__.py')

desc_file = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = ''

if os.path.isfile(desc_file):
    long_description = open(desc_file).read()

setup(name="exemelopy",
      description="exemelopy is a tool for building XML from native "
      "Python data-types, similiar to the json/simplejson modules",
      long_description=long_description,
      version=__version__,
      url="https://github.com/OldhamMade/exemelopy",
      download_url="https://github.com/OldhamMade/exemelopy/"
      "archive/master.zip",
      author=__author__,
      author_email=__author_email__,
      packages=find_packages(exclude=["specs", "benchmark"]),
      install_requires=[
          'lxml',
          'ordereddict'
      ],
      )
