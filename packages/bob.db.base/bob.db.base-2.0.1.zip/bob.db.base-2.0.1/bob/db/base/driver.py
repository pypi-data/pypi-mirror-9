#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 13 Aug 2012 16:19:18 CEST

"""This module defines, among other less important constructions, a management
interface that can be used by Bob to display information about the database and
manage installed files.
"""

import os
import abc

def dbshell(arguments):
  """Drops you into a database shell"""

  if len(arguments.files) != 1:
    raise RuntimeError("Something is wrong this database is supposed to be of type SQLite, but you have more than one data file available: %s" % argument.files)

  if arguments.type == 'sqlite':
    prog = 'sqlite3'
  else:
    raise RuntimeError("Error auxiliary database file '%s' cannot be used to initiate a database shell connection (type='%s')" % (dbfile, arguments.type))

  cmdline = [prog, arguments.files[0]]

  import subprocess

  try:
    if arguments.dryrun:
      print("[dry-run] exec '%s'" % ' '.join(cmdline))
      return 0
    else:
      p = subprocess.Popen(cmdline)
  except OSError as e:
    # occurs when the file is not executable or not found
    print("Error executing '%s': %s (%d)" % (' '.join(cmdline), e.strerror,
        e.errno))
    import sys
    sys.exit(e.errno)

  try:
    p.communicate()
  except KeyboardInterrupt: # the user CTRL-C'ed
    import signal
    os.kill(p.pid, signal.SIGTERM)
    return signal.SIGTERM

  return p.returncode

def dbshell_command(subparsers):
  """Adds a new dbshell subcommand to your subparser"""

  parser = subparsers.add_parser('dbshell', help=dbshell.__doc__)
  parser.add_argument("-n", "--dry-run", dest="dryrun", default=False,
      action='store_true',
      help="does not actually run, just prints what would do instead")
  parser.set_defaults(func=dbshell)


def upload(arguments):
  """For SQLite databases: uploads the db.sql3 database file to a server."""
  # get the file name of the target db
  assert len(arguments.files) == 1
  assert os.path.basename(arguments.files[0]) == 'db.sql3'
  source_file = arguments.files[0]
  target_file = os.path.join(arguments.destination, arguments.name + ".tar.bz2")

  if os.path.exists(source_file):
    print ("Compressing file '%s' to '%s'" %(source_file, target_file))
    import tarfile, stat
    f = tarfile.open(target_file, 'w:bz2')
    f.add(source_file, os.path.basename(source_file))
    f.close()
    os.chmod(target_file, stat.S_IRUSR|stat.S_IWUSR | stat.S_IRGRP|stat.S_IWGRP | stat.S_IROTH)
  else:
    print ("WARNING! Database file '%s' is not available. Did you run 'bob_dbmanage %s create' ?" % (source_file, arguments.name))

def upload_command(subparsers):
  """Adds a new 'upload' subcommand to your parser"""

  parser = subparsers.add_parser('upload', help=upload.__doc__)
  parser.add_argument("--destination", default="/idiap/group/torch5spro/databases/latest")
  parser.set_defaults(func=upload)

  return parser


def download(arguments):
  """For SQLite databases: Downloads the db.sql3 database file from a server."""
  # get the file name of the target db
  assert len(arguments.files) == 1
  assert os.path.basename(arguments.files[0]) == 'db.sql3'
  target_file = arguments.files[0]
  if os.path.exists(target_file) and not arguments.force:
    print ("Skipping download of file '%s' since it exists already." % target_file)
  else:
    # get URL of database file
    source_url = os.path.join(arguments.source, arguments.name + ".tar.bz2")
    # download
    import sys, tempfile, tarfile
    if sys.version_info[0] <= 2:
      import urllib2 as urllib
    else:
      import urllib.request as urllib

    try:
      print ("Extracting url '%s' to '%s'" %(source_url, target_file))
      u = urllib.urlopen(source_url)
      f = tempfile.NamedTemporaryFile(suffix = ".tar.bz2")
      open(f.name, 'wb').write(u.read())
      t = tarfile.open(fileobj=f, mode = 'r:bz2')
      t.extract(os.path.basename(target_file), os.path.dirname(target_file))
      t.close()
      f.close()
    except Exception as e:
      print ("Error while downloading: '%s'" % e)

def download_command(subparsers):
  """Adds a new 'download' subcommand to your parser"""

  parser = subparsers.add_parser('download', help=download.__doc__)
  parser.add_argument("--source", default="http://www.idiap.ch/software/bob/databases/latest/")
  parser.add_argument("--force", action='store_true', help = "Overwrite existing database files?")
  parser.set_defaults(func=download)

  return parser


def print_files(arguments):
  """Prints the current location of raw database files."""

  print ("Files for database '%s':" % arguments.name)
  for k in arguments.files: print(k)

  return 0

def files_command(subparsers):
  """Adds a new 'files' subcommand to your parser"""

  parser = subparsers.add_parser('files', help=print_files.__doc__)
  parser.set_defaults(func=print_files)

  return parser


def version(arguments):
  """Outputs the database version"""

  print('%s == %s' % (arguments.name, arguments.version))

  return 0

def version_command(subparsers):

  parser = subparsers.add_parser('version', help=version.__doc__)
  parser.set_defaults(func=version)

  return parser

def with_metaclass(meta, *bases):
  """Create a base class with a metaclass (works with Python2 and Python3)."""

  return meta("NewBase", bases, {})

class Interface(with_metaclass(abc.ABCMeta, object)):
  """Base manager for Bob databases"""

  @abc.abstractmethod
  def name(self):
    '''Returns a simple name for this database, w/o funny characters, spaces'''
    return

  @abc.abstractmethod
  def files(self):
    '''Returns a python iterable with all auxiliary files needed.

    The values should be take w.r.t. where the python file that declares the
    database is sitting at.
    '''
    return

  @abc.abstractmethod
  def version(self):
    '''Returns the current version number defined in setup.py'''
    return

  @abc.abstractmethod
  def type(self):
    '''Returns the type of auxiliary files you have for this database

    If you return 'sqlite', then we append special actions such as 'dbshell'
    on 'bob_dbmanage.py' automatically for you. Otherwise, we don't.

    If you use auxiliary text files, just return 'text'. We may provide
    special services for those types in the future.

    Use the special name 'builtin' if this database is an integral part of Bob.
    '''
    return

  def setup_parser(self, parser, short_description, long_description):
    '''Sets up the base parser for this database.

    Keyword arguments:

    short_description
      A short description (one-liner) for this database

    long_description
      A more involved explanation of this database

    Returns a subparser, ready to be added commands on
    '''

    from argparse import RawDescriptionHelpFormatter

    # creates a top-level parser for this database
    top_level = parser.add_parser(self.name(),
        formatter_class=RawDescriptionHelpFormatter,
        help=short_description, description=long_description)

    type = self.type()
    files = self.files()

    top_level.set_defaults(name=self.name())
    top_level.set_defaults(version=self.version())
    top_level.set_defaults(type=type)
    top_level.set_defaults(files=files)

    subparsers = top_level.add_subparsers(title="subcommands")

    # adds some stock commands
    version_command(subparsers)

    if type in ('sqlite',):
      dbshell_command(subparsers)
      upload_command(subparsers)
      download_command(subparsers)

    if files is not None:
      files_command(subparsers)

    return subparsers

  @abc.abstractmethod
  def add_commands(self, parser):
    '''Adds commands to a given (:py:mod:`argparse`) parser.

    This method, effectively, allows you to define special commands that your
    database will be able to perform when called from the common driver like
    for example ``create`` or ``checkfiles``.

    You are not obliged to overwrite this method. If you do, you will have the
    chance to establish your own commands. You don't have to worry about stock
    commands such as :py:meth:`files` or :py:meth:`version`. They will be automatically
    hooked-in depending on the values you return for :py:meth:`type` and
    :py:meth:`files`.

    Keyword arguments

    parser
      An instance of a :py:class:`argparse.ArgumentParser` that you can customize, i.e., call
      :py:meth:`argparse.ArgumentParser.add_argument` on.
    '''
    return

__all__ = ('Interface',)
