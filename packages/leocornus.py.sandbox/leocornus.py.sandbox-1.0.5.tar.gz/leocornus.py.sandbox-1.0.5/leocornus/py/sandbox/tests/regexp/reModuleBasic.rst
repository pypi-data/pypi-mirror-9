re Module in Basic

Trying to explore the basic regular expression operation in Python.

Import module::

  >>> import re

Testing find all emails::

  >>> emails = "hello email.one@example.com and email.two@test.com"
  >>> lst = re.findall('\S+@\S+', emails)
  >>> print(lst)
  ['email.one@example.com', 'email.two@test.com']
