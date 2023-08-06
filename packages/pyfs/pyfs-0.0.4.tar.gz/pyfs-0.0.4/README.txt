Python FS - a pythonic file system wrapper for humans
=====================================================

|Build Status| |Coverage Status| |License|

An easy to use file system wrapper for Python that aims to simplify os,
os.path, os.walk, shutils, fnmatch, etc.

This is under active development!

Installation
------------

Install with the Python Package Manager *pip* with the following
command:

.. code:: bash

    pip install pyfs

Or install from source:

.. code:: bash

    git clone https://github.com/chaosmail/python-fs.git
    cd python-fs
    python setup.py install

Documentation
-------------

First, import the python-fs module.

.. code:: python

    import fs

fs.exists(path)
~~~~~~~~~~~~~~~

Returns True if the *path* exists. Returns False if *path* does not
exist.

.. code:: python

    >>> fs.exists('test.txt')
    True
    >>> fs.exists('some_directory')
    True

fs.isfile(path)
~~~~~~~~~~~~~~~

Returns True if the *path* exists and is a file. Returns False if *path*
is a directory or does not exist.

.. code:: python

    >>> fs.isfile('test.txt')
    True
    >>> fs.isfile('some_directory')
    False

fs.isdir(path)
~~~~~~~~~~~~~~

Returns True if the *path* exists and is a directory. Returns False if
*path* is a file or does not exist.

.. code:: python

    >>> fs.isdir('test.txt')
    False
    >>> fs.isdir('some_directory')
    True

fs.stat(path)
~~~~~~~~~~~~~

Returns a `stats
object <https://docs.python.org/2/library/os.html#os.stat>`__ that
contains meta data of *path* where path can be either a file or
directory. Raises *OSError* exception if *path* does not exist.

.. code:: python

    >>> s = fs.stat('test.txt')
    >>> s.st_atime
    1428162423.839133
    >>> s.st_mtime
    1427919315.960152
    >>> s.st_ctime
    1427919315.960152

fs.ctime(path)
~~~~~~~~~~~~~~

Platform dependent; returns time of most recent metadata change on Unix,
or the time of creation on Windows of *path* where path can be either a
file or directory. Raises *OSError* exception if *path* does not exist.

.. code:: python

    >>> fs.ctime('test.txt')
    1427919315.960152

fs.atime(path)
~~~~~~~~~~~~~~

Returns time of most recent access of *path* where path can be either a
file or directory. Raises *OSError* exception if *path* does not exist.

.. code:: python

    >>> fs.atime('test.txt')
    1428162423.839133

fs.mtime(path)
~~~~~~~~~~~~~~

Returns time of most recent content modification of *path* where path
can be either a file or directory. Raises *OSError* exception if *path*
does not exist.

.. code:: python

    >>> fs.mtime('test.txt')
    1427919315.960152

fs.rename(oldPath, newPath)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Renames *oldPath* to new *newPath* where *oldPath* can be either a file
or directory. Raises *OSError* exception if *oldPath* does not exist.

.. code:: python

    >>> fs.rename('old_test.txt', 'new_test.txt')
    >>> fs.rename('old_directory', 'new_directory')

fs.truncate(path)
~~~~~~~~~~~~~~~~~

Removes all files from the *path* directory.

.. code:: python

    >>> fs.truncate('some_directory')

fs.chdir(path)
~~~~~~~~~~~~~~

Changes the current directory to *path*.

.. code:: python

    >>> fs.chdir('some_directory')

fs.cwd()
~~~~~~~~

Get the current working directory.

.. code:: python

    >>> fs.cwd()
    '/path/to/directory'

fs.abspath(path)
~~~~~~~~~~~~~~~~

Returns the absolute path from a relative *path* where *path* can be
either file or directory.

.. code:: python

    >>> fs.abspath('test.txt')
    '/path/to/file/test.txt'
    >>> fs.abspath('some_directory')
    '/path/to/file/some_directory'

fs.normalize(path)
~~~~~~~~~~~~~~~~~~

Returns the normalized path from a *path* where *path* can be either
file or directory.

.. code:: python

    >>> fs.normalize('test_dir/../test/test.txt')
    'test/test.txt'

fs.rm(path)
~~~~~~~~~~~

Deletes the file *path*. Raises an *OSError* exception if the file does
not exist or *path* is a directory.

.. code:: python

    >>> fs.rm('test.txt')

The Unix-like *fs.unlink* is the same as *fs.rm*.

fs.rmdir(path, recursive=True)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deletes the directory *path* with all containing files and directories.
Raises an *OSError* exception if the directory does not exist or *path*
is a file.

.. code:: python

    >>> fs.rmdir('some_directory')

fs.rmfiles(paths)
~~~~~~~~~~~~~~~~~

Deletes an array of files *paths*. Raises an *OSError* exception if a
file does not exist or an element of *paths* is a directory.

.. code:: python

    >>> fs.rmfiles(['test.txt', 'another_file.txt'])

Example: *Remove all files from the current directory*:

.. code:: python

    >>> fs.rmfiles( fs.list() )

Example: *Remove all .pyc files from a directory*:

.. code:: python

    >>> fs.rmfiles( fs.find('*.pyc') )

fs.rmdirs(paths, recursive=True)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deletes an array of directories *paths* with all containing files and
directories. Raises an *OSError* exception if a directory does not exist
or an element of *paths* is a file.

.. code:: python

    >>> fs.rmdirs(['some_directory', 'some_other_dir'])

Example: *Remove all directories from the current directory*:

.. code:: python

    >>> fs.rmdirs( fs.listdirs() )

Example: *Remove all directories that start with local\_*:

.. code:: python

    >>> fs.rmdirs( fs.finddirs('local_*') )

fs.touch(path)
~~~~~~~~~~~~~~

Sets the modification timestamp of *path* to the current time or creates
the file if *path* does not exist. Directories not supported on Windows.

.. code:: python

    >>> fs.touch('test.txt')

fs.list(path='.')
~~~~~~~~~~~~~~~~~

Generator the returns all files that are contained in the directory
*path*. Raises an *OSError* exception if the directory *path* does not
exist.

.. code:: python

    >>> files = fs.list()
    >>> list(files)
    ['test.txt']
    >>> files = fs.list('some_directory')
    >>> list(files)
    ['/path/to/dir/some_directory/another_test.txt']

Example: *Loop over all files in the current directory*:

.. code:: python

    >>> for filename in fs.list():
            pass

fs.listdirs(path='.')
~~~~~~~~~~~~~~~~~~~~~

Generator the returns all directories that are contained in the
directory *path*. Raises an *OSError* exception if the directory *path*
does not exist.

.. code:: python

    >>> dirs = fs.listdirs()
    >>> list(dirs)
    ['some_directory']
    >>> dirs = fs.listdirs('some_directory')
    >>> list(dirs)
    []

Example: *Loop over all directories in the current directory*:

.. code:: python

    >>> for dirname in fs.listdirs():
            pass

fs.find(pattern, path='.', exclude=None, recursive=True)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generator the returns all files that match *pattern* and are contained
in the directory *path*. Both *pattern* and *exclude* can be `Unix
shell-style
wildcards <https://docs.python.org/3.4/library/fnmatch.html>`__ or
arrays of wildcards. Raises an *OSError* exception if the directory
*path* does not exist.

.. code:: python

    >>> files = fs.find('*.txt')
    >>> list(files)
    ['/path/to/file/test.txt', '/path/to/file/some_directory/another_test.txt']
    >>> files = fs.find('*.txt', exclude='another*')
    >>> list(files)
    ['/path/to/file/test.txt']

Example: *Loop over all .csv files in the current directory*:

.. code:: python

    >>> for filename in fs.find('*.csv', recursive=False):
            pass

Example: *Loop over all .xls and .xlsx files in the current directory
and all sub-directories*:

.. code:: python

    >>> for filename in fs.find(['*.xls', '*.xlsx']):
            pass

Example: *Loop over all .ini files in the config directory and all
sub-directories except the ones starting with local\_*:

.. code:: python

    >>> for filename in fs.find('*.ini', path='config', exclude='local_*'):
            pass

Example: *Find and get the Vagrantfile in the config directory*:

.. code:: python

    >>> filename = next( fs.find('Vagrantfile', path='config'), None)

Example: *Find the latest SQL file in the backups directory*:

.. code:: python

    >>> filename = max( fs.find('*.sql', path='backup'), key=fs.ctime)

fs.finddirs(pattern, path='.', exclude=None, recursive=True)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generator the returns all directories that match *pattern* and are
contained in the directory *path*. Both *pattern* and *exclude* can be
`Unix shell-style
wildcards <https://docs.python.org/3.4/library/fnmatch.html>`__ or
arrays of wildcards. Raises an *OSError* exception if the directory
*path* does not exist.

.. code:: python

    >>> dirs = fs.finddirs('some*')
    >>> list(dirs)
    ['/path/to/file/some_directory']
    >>> dirs = fs.finddirs('some*', exclude='*directory')
    >>> list(dirs)
    []

Example: *Loop over all .git directories in the current directory and
all subdirectories*:

.. code:: python

    >>> for dir in fs.finddirs('.git'):
            pass

fs.open(path, mode='r')
~~~~~~~~~~~~~~~~~~~~~~~

Returns a `file
object <https://docs.python.org/2/library/stdtypes.html#bltin-file-objects>`__
of a file *path*. Raises an *IOError* exception if the file *path* does
not exist.

.. code:: python

    >>> file = fs.open('text.txt')

Example: *Loop through the lines of a file*

.. code:: python

    >>> file = fs.open('config.ini', 'r')
    >>> for line in file:
            pass

fs.read(path, encoding='UTF-8')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reads and returns the content of a file *path*. Raises an *IOError*
exception if the file *path* does not exist.

.. code:: python

    >>> fs.read('text.txt')
    u'test'

fs.write(path, content, encoding='UTF-8', append=False, raw=False)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Writes the content *content* of a file *path*.

.. code:: python

    >>> fs.write('text.txt', 'test')

Example: *Append content to a file*

.. code:: python

    >>> fs.write('text.txt', 'test', append=True)

Example: *Download an image from an url using
`requests <http://docs.python-requests.org/en/latest/>`__ and save it to
local disc*:

.. code:: python

    >>> import requests
    >>> res = requests.get(url, stream=True)
    >>> fs.write(path, res.raw, raw=True)

fs.sep
~~~~~~

The character used by the operating system to separate pathname
components. This is '/' for POSIX and '\\\\' for Windows.

.. code:: python

    >>> fs.sep
    '/'

fs.join(paths)
~~~~~~~~~~~~~~

Joins an array of *parts* with *fs.sep*.

.. code:: python

    >>> fs.join([fs.sep, 'path', 'to', 'directory'])
    '/path/to/directory'

Additionally, you can also pass the path elements as arguments
*fs.join(path, path, ...)*.

.. code:: python

    >>> fs.join(fs.sep, 'path', 'to', 'directory')
    '/path/to/directory'

fs.extname(path)
~~~~~~~~~~~~~~~~

Returns the extension name of a file *path*.

.. code:: python

    >>> fs.extname('/path/to/file/test.txt')
    '.txt'

fs.basename(path, ext="")
~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the base name of a file *path*.

.. code:: python

    >>> fs.basename('/path/to/file/test.txt')
    'test.txt'
    >>> fs.basename('/path/to/file/test.txt', '.txt')
    'test'

fs.dirname(path)
~~~~~~~~~~~~~~~~

Returns the directory name of a file *path*.

.. code:: python

    >>> fs.dirname('/path/to/file/test.txt')
    '/path/to/file'

Changelog
---------

0.0.4
~~~~~

-  Fixed errors with fs.find for recurive=False
-  Added tests for fs.find and fs.finddirs
-  Added coverage badge

0.0.3
~~~~~

-  Fixed python3 error with fs.read
-  Added tests for fs.write and fs.read

0.0.2
~~~~~

-  Fixed installation error from missing README.md file

0.0.1
~~~~~

-  Initial upload to PyPi

License
-------

This software is provided under the MIT License.

.. |Build Status| image:: https://travis-ci.org/chaosmail/python-fs.svg?branch=master
   :target: https://travis-ci.org/chaosmail/python-fs
.. |Coverage Status| image:: https://coveralls.io/repos/chaosmail/python-fs/badge.svg
   :target: https://coveralls.io/r/chaosmail/python-fs
.. |License| image:: http://img.shields.io/:license-mit-blue.svg
   :target: https://raw.githubusercontent.com/chaosmail/python-fs/master/LICENSE
