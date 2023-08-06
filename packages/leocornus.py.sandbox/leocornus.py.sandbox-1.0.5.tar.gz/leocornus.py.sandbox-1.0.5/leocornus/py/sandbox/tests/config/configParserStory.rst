Story for ConfigParser
======================

.. note::

   the ConfigParser_ module has been renmae to configparser_ in 
   Python 3. the 2to3_ tool will automatically adapt imports
   when converting your sources to Python 3.

As of the module name change, we will using the following way 
to import configparser module::

  >>> try:
  ...     import ConfigParser as configparser
  ... except ImportError:
  ...     import configparser

Create a ConfigParser object::

  >>> config = configparser.ConfigParser()
  >>> config.sections()
  []

.. _ConfigParser: https://docs.python.org/2/library/configparser.html
.. _configparser: https://docs.python.org/3/library/configparser.html
.. _2to3: https://docs.python.org/2/glossary.html#term-to3
