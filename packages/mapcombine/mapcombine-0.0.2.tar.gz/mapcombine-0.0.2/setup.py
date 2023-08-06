#!/usr/bin/env python

from os.path import exists
from setuptools import setup
import re

version_raw    = open('mapcombine/_version.py').read()
version_regex  = r"^__version__ = ['\"]([^'\"]*)['\"]"
version_result = re.search(version_regex, version_raw, re.M)
if version_result:
    version_string = version_result.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='mapcombine',
      version=version_string,
      description='Simple combine-centric MapReduce',
      url='http://github.com/maxhutch/mapcombine/',
      author='https://raw.github.com/maxhutch/mapcombine/master/AUTHORS.md',
      author_email='maxhutch@gmail.com',
      maintainer='Max Hutchinson',
      maintainer_email='maxhutch@gmail.com',
      license='MIT',
      keywords='MapReduce',
      packages=['mapcombine'],
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      zip_safe=True)
