# Utility functions for py2deb.
#
# Authors:
#  - Arjan Verwer
#  - Peter Odding <peter.odding@paylogic.com>
# Last Change: March 4, 2015
# URL: https://py2deb.readthedocs.org

"""
The :py:mod:`py2deb.utils` module contains miscellaneous code.
"""

# Standard library modules.
import logging
import re
import shutil
import sys
import tempfile

# External dependencies.
from cached_property import cached_property
from deb_pkg_tools.package import find_package_archives
from six import BytesIO

# Initialize a logger.
logger = logging.getLogger(__name__)


class PackageRepository(object):

    """
    Very simply abstraction for a directory containing ``*.deb`` archives.

    Used by :py:class:`py2deb.converter.PackageConverter` to recognize which
    Python packages have previously been converted (and so can be skipped).
    """

    def __init__(self, directory):
        """
        Initialize a :py:class:`PackageRepository` object.

        :param directory: The pathname of the directory containing ``*.deb``
                          archives (a string).
        """
        self.directory = directory

    @cached_property
    def archives(self):
        """
        Find archive(s) in package repository / directory.

        :returns: A sorted list of package archives, same as the return value
                  of :py:func:`deb_pkg_tools.package.find_package_archives()`.

        An example:

        >>> from py2deb import PackageRepository
        >>> repo = PackageRepository('/tmp')
        >>> repo.archives
        [PackageFile(name='py2deb', version='0.1', architecture='all',
                     filename='/tmp/py2deb_0.1_all.deb'),
         PackageFile(name='py2deb-cached-property', version='0.1.5', architecture='all',
                     filename='/tmp/py2deb-cached-property_0.1.5_all.deb'),
         PackageFile(name='py2deb-chardet', version='2.2.1', architecture='all',
                     filename='/tmp/py2deb-chardet_2.2.1_all.deb'),
         PackageFile(name='py2deb-coloredlogs', version='0.5', architecture='all',
                     filename='/tmp/py2deb-coloredlogs_0.5_all.deb'),
         PackageFile(name='py2deb-deb-pkg-tools', version='1.20.4', architecture='all',
                     filename='/tmp/py2deb-deb-pkg-tools_1.20.4_all.deb'),
         PackageFile(name='py2deb-docutils', version='0.11', architecture='all',
                     filename='/tmp/py2deb-docutils_0.11_all.deb'),
         PackageFile(name='py2deb-executor', version='1.2', architecture='all',
                     filename='/tmp/py2deb-executor_1.2_all.deb'),
         PackageFile(name='py2deb-html2text', version='2014.4.5', architecture='all',
                     filename='/tmp/py2deb-html2text_2014.4.5_all.deb'),
         PackageFile(name='py2deb-humanfriendly', version='1.8.2', architecture='all',
                     filename='/tmp/py2deb-humanfriendly_1.8.2_all.deb'),
         PackageFile(name='py2deb-pkginfo', version='1.1', architecture='all',
                     filename='/tmp/py2deb-pkginfo_1.1_all.deb'),
         PackageFile(name='py2deb-python-debian', version='0.1.21-nmu2', architecture='all',
                     filename='/tmp/py2deb-python-debian_0.1.21-nmu2_all.deb'),
         PackageFile(name='py2deb-six', version='1.6.1', architecture='all',
                     filename='/tmp/py2deb-six_1.6.1_all.deb')]

        """
        return find_package_archives(self.directory)

    def get_package(self, package, version, architecture):
        """
        Find a package in the repository.

        Here's an example:

        >>> from py2deb import PackageRepository
        >>> repo = PackageRepository('/tmp')
        >>> repo.get_package('py2deb', '0.1', 'all')
        PackageFile(name='py2deb', version='0.1', architecture='all', filename='/tmp/py2deb_0.1_all.deb')

        :param package: The name of the package (a string).
        :param version: The version of the package (a string).
        :param architecture: The architecture of the package (a string).
        :returns: A :py:class:`deb_pkg_tools.package.PackageFile` object
                  or ``None``.
        """
        for archive in self.archives:
            if (archive.name == package and archive.version == version and archive.architecture == architecture):
                return archive


class TemporaryDirectory(object):

    """
    Easy temporary directory creation & cleanup using the :keyword:`with` statement.

    Here's an example of how to use this:

    .. code-block:: python

       with TemporaryDirectory() as directory:
           # Do something useful here.
           assert os.path.isdir(directory)
    """

    def __init__(self, **options):
        """
        Initialize context manager that manages creation & cleanup of temporary directory.

        :param options: Any keyword arguments are passed on to
                        :py:func:`tempfile.mkdtemp()`.
        """
        self.options = options

    def __enter__(self):
        """
        Create the temporary directory.
        """
        self.temporary_directory = tempfile.mkdtemp(**self.options)
        logger.debug("Created temporary directory: %s", self.temporary_directory)
        return self.temporary_directory

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Destroy the temporary directory.
        """
        logger.debug("Cleaning up temporary directory: %s", self.temporary_directory)
        shutil.rmtree(self.temporary_directory)
        del self.temporary_directory


def python_version():
    """
    Find the version of Python we're running.

    This specifically returns a name matching the format of the names of the
    Debian packages providing the various available Python versions.

    :returns: A string like ``python2.6`` or ``python2.7``.
    """
    python_version = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
    logger.debug("Detected Python version: %s", python_version)
    return python_version


def normalize_package_name(python_package_name):
    """
    Normalize Python package name to be used as Debian package name.

    :param python_package_name: The name of a Python package
                                as found on PyPI (a string).
    :returns: The normalized name (a string).

    >>> from py2deb import normalize_package_name
    >>> normalize_package_name('MySQL-python')
    'mysql-python'
    >>> normalize_package_name('simple_json')
    'simple-json'
    """
    return re.sub('[^a-z0-9]+', '-', python_package_name.lower()).strip('-')


def normalize_package_version(python_package_version):
    """
    Normalize Python package version to be used as Debian package version.

    :param python_package_version: The version of a Python package (a string).

    Reformats Python package versions to comply with the Debian policy manual.
    All characters except alphanumerics, dot (``.``) and plus (``+``) are
    replaced with dashes (``-``).
    """
    sanitized_version = re.sub('[^a-z0-9.+]+', '-', python_package_version.lower()).strip('-')
    components = sanitized_version.split('-')
    # Make sure the "Debian revision" contains a digit.
    if len(components) > 1 and not re.search('[0-9]', components[-1]):
        components.append('1')
        sanitized_version = '-'.join(components)
    return sanitized_version


def package_names_match(a, b):
    """
    Check whether two Python package names are equal.

    Uses :py:func:`normalize_package_name()` to normalize both names before
    comparing them for equality. This makes sure differences in case and dashes
    versus underscores are ignored.

    :param a: The name of the first Python package (a string).
    :param b: The name of the second Python package (a string).
    :returns: ``True`` if the package names match, ``False`` if they don't.
    """
    return normalize_package_name(a) == normalize_package_name(b)


def compact_repeating_words(words):
    """
    Remove adjacent repeating words.

    :param words: An iterable of words (strings), assumed to already be
                  normalized (lowercased).
    :returns: An iterable of words with adjacent repeating words replaced by a
              single word.

    This is used to avoid awkward word repetitions in the package name
    conversion algorithm. Here's an example of what I mean:

    >>> from py2deb import compact_repeating_words
    >>> name_prefix = 'python'
    >>> package_name = 'python-mcrypt'
    >>> combined_words = [name_prefix] + package_name.split('-')
    >>> print(list(combined_words))
    ['python', 'python', 'mcrypt']
    >>> compacted_words = compact_repeating_words(combined_words)
    >>> print(list(compacted_words))
    ['python', 'mcrypt']
    """
    last_word = None
    for word in words:
        if word != last_word:
            yield word
        last_word = word


def embed_install_prefix(handle, install_prefix):
    """
    Embed Python snippet that adds custom installation prefix to module search path.

    :param handle: A file-like object containing an executable Python script.
    :param install_prefix: The pathname of the custom installation prefix (a string).
    :returns: A file-like object containing the modified Python script.
    """
    lines = handle.readlines()
    # Make sure the first line of the file contains something that looks like a
    # Python hashbang so we don't try to embed Python code in files like shell
    # scripts :-). Note that the regular expression pattern is very
    # unrestrictive on purpose.
    if lines and re.match(b'^#!.*\\bpython', lines[0]):
        # We need to choose where to inject our line into the Python script.
        # This is trickier than it might seem at first, because of conflicting
        # concerns:
        #
        # 1) We want our line to be the first one to be executed so that any
        #    later imports respect the custom installation prefix.
        #
        # 2) Our line cannot be the very first line because we would break the
        #    hashbang of the script, without which it won't be executable.
        #
        # 3) Python has the somewhat obscure `from __future__ import ...'
        #    statement which must precede all other statements.
        #
        # Our first step is to skip all comments, taking care of point two.
        insertion_point = 0
        while insertion_point < len(lines) and lines[insertion_point].startswith(b'#'):
            insertion_point += 1
        # The next step is to bump the insertion point if we find any `from
        # __future__ import ...' statements.
        for i, line in enumerate(lines):
            if re.match(b'^\\s*from\\s+__future__\\s+import\\s+', line):
                insertion_point = i + 1
        lines.insert(insertion_point, ('import sys; sys.path.insert(0, %r)\n' % install_prefix).encode('UTF-8'))
        # Turn the modified contents back into a file-like object.
        handle = BytesIO(b''.join(lines))
    return handle
