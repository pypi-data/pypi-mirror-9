#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.mixin.ucattrs',
  description = "Mixin for .FOO uppercase attributes mapped to ['FOO'] access.",
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150118',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u"A mixin and a dict subclass where .FOO means ['FOO']\n----------------------------------------------------\n\nPresents:\n\n* WithUC_Attrs, a mixin for other classes which provides .__getattr__ and .__setattr__ which intercept .FOO where FOO would match the rexgep ``^[A-Z][_A-Z0-9]*$`` and maps them to ['FOO'].\n\n* UCdict, a subclass of dict using the WithUC_Attrs mixin.\n",
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.mixin.ucattrs'],
)
