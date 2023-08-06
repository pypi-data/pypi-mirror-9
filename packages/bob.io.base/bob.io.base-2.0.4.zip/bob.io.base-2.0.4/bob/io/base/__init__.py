# import Libraries of other lib packages
import bob.core

# import our own Library
import bob.extension
bob.extension.load_bob_library('bob.io.base', __file__)

from ._library import File, HDF5File, extensions
from . import version
from .version import module as __version__
from .version import api as __api_version__

import os

def __is_string__(s):
  """Returns ``True`` if the given object is a string

  This method can be used with Python-2.x or 3.x and returns a string
  respecting each environment's constraints.
  """

  from sys import version_info

  return (version_info[0] < 3 and isinstance(s, (str, unicode))) or \
    isinstance(s, (bytes, str))

def create_directories_safe(directory, dryrun=False):
  """Creates a directory if it does not exists, with concurrent access support.
  This function will also create any parent directories that might be required.
  If the dryrun option is selected, it does not actually create the directory,
  but just writes the (Linux) command that would have been executed.

  Parameters:

  directory
    The directory that you want to create.

  dryrun
    Only write the command, but do not execute it.
  """
  try:
    if dryrun:
      print("[dry-run] mkdir -p '%s'" % directory)
    else:
      if directory and not os.path.exists(directory): os.makedirs(directory)

  except OSError as exc: # Python >2.5
    import errno
    if exc.errno != errno.EEXIST:
      raise


def load(inputs):
  """Loads the contents of a file, an iterable of files, or an iterable of
  :py:class:`bob.io.base.File`'s into a :py:class:`numpy.ndarray`.

  Parameters:

  inputs

    This might represent several different entities:

    1. The name of a file (full path) from where to load the data. In this
       case, this assumes that the file contains an array and returns a loaded
       numpy ndarray.
    2. An iterable of filenames to be loaded in memory. In this case, this
       would assume that each file contains a single 1D sample or a set of 1D
       samples, load them in memory and concatenate them into a single and
       returned 2D numpy ndarray.
    3. An iterable of :py:class:`bob.io.base.File`. In this case, this would assume
       that each :py:class:`bob.io.base.File` contains a single 1D sample or a set
       of 1D samples, load them in memory if required and concatenate them into
       a single and returned 2D numpy ndarray.
    4. An iterable with mixed filenames and :py:class:`bob.io.base.File`. In this
       case, this would returned a 2D :py:class:`numpy.ndarray`, as described
       by points 2 and 3 above.
  """

  from collections import Iterable
  import numpy
  if __is_string__(inputs):
    return File(inputs, 'r').read()
  elif isinstance(inputs, Iterable):
    retval = []
    for obj in inputs:
      if __is_string__(obj):
        retval.append(load(obj))
      elif isinstance(obj, File):
        retval.append(obj.read())
      else:
        raise TypeError("Iterable contains an object which is not a filename nor a bob.io.base.File.")
    return numpy.vstack(retval)
  else:
    raise TypeError("Unexpected input object. This function is expecting a filename, or an iterable of filenames and/or bob.io.base.File's")

def merge(filenames):
  """Converts an iterable of filenames into an iterable over read-only
  bob.io.base.File's.

  Parameters:

  filenames

    This might represent:

    1. A single filename. In this case, an iterable with a single
       :py:class:`bob.io.base.File` is returned.
    2. An iterable of filenames to be converted into an iterable of
       :py:class:`bob.io.base.File`'s.
  """

  from collections import Iterable
  from .utils import is_string
  if is_string(filenames):
    return [File(filenames, 'r')]
  elif isinstance(filenames, Iterable):
    return [File(k, 'r') for k in filenames]
  else:
    raise TypeError("Unexpected input object. This function is expecting an iterable of filenames.")

def save(array, filename, create_directories = False):
  """Saves the contents of an array-like object to file.

  Effectively, this is the same as creating a :py:class:`bob.io.base.File` object
  with the mode flag set to `w` (write with truncation) and calling
  :py:meth:`bob.io.base.File.write` passing `array` as parameter.

  Parameters:

  array
    The array-like object to be saved on the file

  filename
    The name of the file where you need the contents saved to

  create_directories
    Automatically generate the directories if required
  """
  # create directory if not existent yet
  if create_directories:
    create_directories_safe(os.path.dirname(filename))

  return File(filename, 'w').write(array)

# Just to make it homogenous with the C++ API
write = save
read = load

def append(array, filename):
  """Appends the contents of an array-like object to file.

  Effectively, this is the same as creating a :py:class:`bob.io.base.File` object
  with the mode flag set to `a` (append) and calling
  :py:meth:`bob.io.base.File.append` passing `array` as parameter.

  Parameters:

  array
    The array-like object to be saved on the file

  filename
    The name of the file where you need the contents saved to
  """
  return File(filename, 'a').append(array)

def peek(filename):
  """Returns the type of array (frame or sample) saved in the given file.

  Effectively, this is the same as creating a :py:class:`bob.io.base.File` object
  with the mode flag set to `r` (read-only) and returning
  :py:func:`bob.io.base.File.describe`.

  Parameters:

  filename
    The name of the file to peek information from
  """
  return File(filename, 'r').describe()

def peek_all(filename):
  """Returns the type of array (for full readouts) saved in the given file.

  Effectively, this is the same as creating a :py:class:`bob.io.base.File` object
  with the mode flag set to `r` (read-only) and returning
  ``bob.io.base.File.describe(all=True)``.

  Parameters:

  filename
    The name of the file to peek information from
  """
  return File(filename, 'r').describe(all=True)

# Keeps compatibility with the previously existing API
open = File

def get_config():
  """Returns a string containing the configuration information.
  """

  import pkg_resources
  from .version import externals

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s [api=0x%04x] (%s)\n" % (this.key, this.version,
      __api_version__, this.location)
  retval += "  - c/c++ dependencies:\n"
  for k in sorted(externals): retval += "    - %s: %s\n" % (k, externals[k])
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()


def get_include_directories():
  """Returns a list of include directories for dependent libraries, such as HDF5."""
  from bob.extension import pkgconfig
  # try to use pkg_config first
  try:
    from bob.extension.utils import find_header
    # locate pkg-config on our own
    header = 'hdf5.h'
    candidates = find_header(header)
    if not candidates:
      raise RuntimeError("could not find %s's `%s' - have you installed %s on this machine?" % ('hdf5', header, 'hdf5'))

    return [os.path.dirname(candidates[0])]
  except RuntimeError:
    pkg = pkgconfig('hdf5')
    return pkg.include_directories()



# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
