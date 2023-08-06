Python Basic
============

Get to know Python language in basic.

.. contents:: Table of Contents
   :depth: 5

Basic Operation
---------------

Obervious things::

  >>> 1 + 3
  4
  >>> a = [1, 2, 3]
  >>> sum(a)
  6

Basic os Module
---------------

Import the os module::

  >>> import os

How to find current user's home folder::

  >>> homeFolder = os.path.expanduser('~')

The **__file__** gives details infor about current file::

  >>> print(__file__)
  /.../leocornus/py/sandbox/tests/basicPython.rst
  >>> print(os.path.realpath(__file__))
  /.../leocornus/py/sandbox/tests/basicPython.rst
  >>> print('basename: %s' % os.path.basename(__file__))
  basename: basicPython.rst
  >>> print('dirname: %s' % os.path.dirname(__file__))
  dirname: /.../leocornus/py/sandbox/tests

Create a folder::

  >>> testFolder = os.path.join(homeFolder, 'testtmp')
  >>> os.path.exists(testFolder)
  False
  >>> os.mkdir(testFolder)
  >>> os.path.exists(testFolder)
  True

Change current working directory::

  >>> os.chdir(testFolder)

Get current working directory::

  >>> print(os.getcwd()) # doctest: +ELLIPSIS
  /home/.../testtmp
  >>> # need change back to home folder to avoid some
  >>> # error like "cannot access parent directories".
  >>> os.chdir(homeFolder)

createFile
~~~~~~~~~~

utility function to create a file in a folder.
There parameters: folder path, filename, and content for the file.
There is no return value for this function::

  >>> def createFile(folder, filename, content):
  ...     fullName = os.path.join(folder, filename)
  ...     os.system("touch " + fullName)
  ...     f = open(fullName, 'r+')
  ...     f.write(content)
  ...     f.close()

Walk through a directory
~~~~~~~~~~~~~~~~~~~~~~~~

Cases:
  Walk through a directory and all of its sub-directories to 
  find all files with extension **.rst**.

Get ready some testing directories and files::

  >>> dOne = os.path.join(testFolder, 'one')
  >>> dTwo = os.path.join(testFolder, 'two')
  >>> dOneOne = os.path.join(dOne, 'oneone')
  >>> os.mkdir(dOne)
  >>> os.mkdir(dOneOne)
  >>> os.mkdir(dTwo)

create files::

  >>> createFile(testFolder, 'root.rst', '')
  >>> createFile(dOne, 'one.rst', '')
  >>> createFile(dOne, 'one.txt', '')
  >>> createFile(dOneOne, 'oneone.rst', '')
  >>> createFile(dTwo, 'two.rst', '')
  >>> createFile(dTwo, 'two.txt', '')

walk through the testFolder to look for **.rst** files::

  >>> for dirpath, dirnames, filenames in os.walk(testFolder):
  ...     for name in filenames:
  ...         # check the extension.
  ...         if name.endswith('.rst'):
  ...             # norm path for the rst file.
  ...             path = os.path.join(dirpath, name)
  ...             normpath = os.path.normpath(path)
  ...             # normpath is full path.
  ...             print(normpath)
  ...             # try to get the relative path based on testFolder.
  ...             relpath = normpath.split(testFolder)[1][1:]
  ...             print(relpath)
  /home.../root.rst
  root.rst
  /home.../one/one.rst
  one/one.rst
  /home.../one/oneone/oneone.rst
  one/oneone/oneone.rst
  /home.../two/two.rst
  two/two.rst

annot access parent directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To avoid get errors like this::

  shell-init: error retrieving current directory: getcwd: cannot access parent directories: No such file or directory

We need change current directory back to default directory,
which is the home directory.::

  >>> os.chdir(homeFolder)

Basic shutil Module
-------------------

  >>> import shutil

Remove a whole folder, including files and subfolders in it.
This is typically helpful for testing script::

  >>> shutil.rmtree(testFolder)

Basic String Operator
---------------------

Try the splitlines::

  >>> lines = """line one
  ... line two
  ... line three
  ... """
  >>> lines.splitlines()
  ['line one', 'line two', 'line three']

Check a string ends with something::

  >>> aName = 'someting.ends'
  >>> aName.endswith('.ends')
  True
