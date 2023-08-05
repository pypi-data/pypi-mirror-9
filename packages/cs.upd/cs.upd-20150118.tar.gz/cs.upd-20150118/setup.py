#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.upd',
  description = 'single line status updates with minimal update sequences',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150118',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Single line status updates.\n===========================\n\n* Upd: a class accepting update strings which emits minimal test to update a progress line.\n\n-- out(s): update the line to show the string `s`\n\n-- nl(s): flush the output line, write `s` with a newline, restore the status line\n\n-- without(func,...): flush the output line, call func, restore the status line\n\nThis is available as an output mode in cs.logutils.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.upd'],
  requires = ['cs.lex', 'cs.tty'],
)
