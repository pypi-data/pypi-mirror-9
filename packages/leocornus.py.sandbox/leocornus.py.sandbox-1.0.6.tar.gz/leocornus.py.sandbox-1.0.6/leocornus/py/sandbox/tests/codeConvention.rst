Style Guide for Python Code
===========================

Important PEPs:

- `PEP 8`_ Style Guilde for Python Code
- `PEP 257`_ Docstring Conventions

Test Docstring
--------------

Define a simple function to explore how docstring works::

  >>> def testFunc(a, b):
  ...     """Try to return the sum of the inputs.
  ...     """
  ...     return sum([a, b])

Now test the function it self::

  >>> a = 1
  >>> b = 2
  >>> print(testFunc(a, b))
  3

A docstring could be access through the **__doc__** attribute::

  >>> print(testFunc.__doc__)
  Try to return the sum of the inputs.

.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _PEP 257: https://www.python.org/dev/peps/pep-0257/
