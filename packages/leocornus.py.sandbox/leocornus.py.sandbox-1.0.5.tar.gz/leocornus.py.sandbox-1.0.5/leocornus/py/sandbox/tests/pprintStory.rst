Data Pretty Printer Story
=========================

The **pprint** module is a built-in module for Python language to 
print aribitray Python data structure in a pretty and readable form.
The output could be used diretly as input to the Python interpreter.

.. contents:: Table of Contents
  :depth: 5

Basic Usage
-----------

First, we will import the moudle::

  >>> import pprint

You could set the indent size for the output::

  >>> printer = pprint.PrettyPrinter(indent=2)
  >>> printer.pprint(printer) # doctest: +ELLIPSIS
  <pprint.PrettyPrinter instance at 0x...>
  >>> a = [1, 2, 3]
  >>> printer.pprint(a)
  [1, 2, 3]

The following will make a recursive list::

  >>> a.insert(0, a[:])
  >>> printer.pprint(a)
  [[1, 2, 3], 1, 2, 3]

Questions
---------

- The **indent** keywork seems not working!
  Maybe I didn't find the right case.
