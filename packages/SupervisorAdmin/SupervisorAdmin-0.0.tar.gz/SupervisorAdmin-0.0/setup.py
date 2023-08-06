"""
setup packaging script for SupervisorAdmin
"""

import os

version = "0.0"
dependencies = ['which']

# allow use of setuptools/distribute or distutils
kw = {}
try:
    from setuptools import setup
    kw['entry_points'] = """
      [console_scripts]
      supervisor-add = supervisoradmin.add:main
"""
    kw['install_requires'] = dependencies
except ImportError:
    from distutils.core import setup
    kw['requires'] = dependencies

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = ''


setup(name='SupervisorAdmin',
      version=version,
      description="add supervisor jobs",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/SupervisorAdmin',
      license='',
      packages=['supervisoradmin'],
      include_package_data=True,
      zip_safe=False,
      **kw
      )
