'''
cloudelements: SDK for Cloud Elements

Note that "python setup.py test" invokes pytest on the package. With appropriately
configured setup.cfg, this will check both xxx_test modules and docstrings.

Copyright 2015, LeadGenius.
Licensed under MIT.
'''
import sys
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.markdown')).read()
CHANGES = open(os.path.join(here, 'CHANGELOG.txt')).read()
requires = open(os.path.join(here, 'requirements.txt')).read().splitlines()

version = "0.2.1"

setup(name="cloudelements",
      version=version,
      description="SDK for Cloud Elements",
      long_description=README + '\n\n\n' + CHANGES,
      classifiers=[
        'Programming Language :: Python'
      ],
      keywords="", # Separate with spaces
      author="LeadGenius",
      author_email="developer@leadgenius.com",
      url="http://leadgenius.github.com/cloudelements",
      license="MIT",
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      tests_require=['pytest'],
      setup_requires=['setuptools_git'],
      install_requires=requires,
      entry_points={}
)
