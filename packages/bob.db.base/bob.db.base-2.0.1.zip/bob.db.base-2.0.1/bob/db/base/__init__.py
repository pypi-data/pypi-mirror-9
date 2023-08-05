#!/usr/bin/env python
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 23 Jun 20:22:28 2011 CEST
# vim: set fileencoding=utf-8 :

"""The db package contains simplified APIs to access data for various databases
that can be used in Biometry, Machine Learning or Pattern Classification."""

import pkg_resources

__version__ = pkg_resources.require(__name__)[0].version

def get_config():
  """Returns a string containing the configuration information.
  """

  import pkg_resources

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s (%s)\n" % (this.key, this.version, this.location)
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()

from . import utils, driver

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
