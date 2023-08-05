#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.logutils',
  description = 'Logging convenience routines.',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150118',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Logging convenience routines.\n-----------------------------\n\nThe logging package is very useful, but a little painful to use. This package provides low impact logging setup and some extremely useful if unconventional context hooks for logging.\n\nThe logging verbosity output format has different defaults based on whether an output log file is a tty and whether the environment variable $DEBUG is set, and to what.\n\nSome examples:\n--------------\n\nProgram initialisation::\n\n  from cs.logutils import setup_logging\n\n  def main(argv):\n    cmd = os.path.basename(argv.pop(0))\n    setup_logging(cmd)\n\nBasic logging from anywhere::\n\n  from cs.logutils import info, warning, error\n  [...]\n  def some_function(...):\n    [...]\n    error("nastiness found! bad value=%r", bad_value)\n\nContext for log messages and exception strings::\n\n  from cs.logutils import Pfx\n  [...]\n  def func1(foo):\n    [...]\n    with Pfx("func1(%s)", foo.name):\n      [...]\n      warning("badness!")   # emits "func1(fooname): badness!"\n  [...]\n  def loadfile(filename):\n    with Pfx(filename):\n      lineno = 0\n      for line in open(filename):\n        lineno += 1\n        with Pfx("%d", lineno):\n          [...]\n          bah = something from the line ...\n          func1(bah)        # emits "filename: lineno: func1(fooname): badness!"\n                            # if the warning triggers\n\nThis keeps log lines short and provides context in reported errors.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.logutils'],
  requires = ['cs.ansi_colour', 'cs.excutils', 'cs.obj', 'cs.py3'],
)
