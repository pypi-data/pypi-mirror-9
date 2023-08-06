re Module in Basic

Trying to explore the basic regular expression operation in Python.

Import module::

  >>> import re

Testing find all emails::

  >>> emails = "hello email.one@example.com and email.two@test.com"
  >>> lst = re.findall('\S+@\S+', emails)
  >>> print(lst)
  ['email.one@example.com', 'email.two@test.com']

How multi lines string is handled?
----------------------------------

Here is are multi line string::

  >>> lines = """First line red
  ... second line blue
  ... third line yellow and red"""

Pattern to looking for color red or blue::

  >>> colors = re.findall('(red|blue)', lines)

The result will include all lines::

  >>> print(colors)
  ['red', 'blue', 'red']

Search and Replace
------------------

Testing this lines of strings::

  >>> source = """{{Feature Infobox
  ... |name=Plugin One
  ... |name=Plugin Two|type=something
  ... |internet_page=[http://www.plugin.com Plugin Homepage]
  ... |description=plugin description.kkkk
  ... |latest_version=1.0.1
  ... |download=[http://10.1.1.1/repo/one.1.0.1.zip one.1.0.1.zip]}}
  ... other content.
  ... """

try to replace new line with empty string, 
only for the template content
::

  >>> p = re.compile('\\n\|')
  >>> onelinesrc = p.sub('|', source)
  >>> print(onelinesrc)
  {{Feature Infobox|name=Plugin One...}}
  other content.

get the template source in one line.
::

  >>> p = re.compile('{{(.*)}}')
  >>> temps = p.findall(onelinesrc)
  >>> print(temps)
  ['Feature Infobox|name=Plu...zip]']
  >>> oneline = temps[0]
  >>> print(oneline)
  Feature Infobox|name=Plu...zip]

replace **\|** with new line **\n|**, this is the standard format.
::

  >>> p = re.compile('\|')
  >>> lines = p.sub('\\n|', oneline)
  >>> print(lines)
  Feature Infobox
  |name=Plugin One
  ...

find all pattern like **key=value** from the oneline source::

  >>> p = re.compile('name=.*')
  >>> names = p.findall(lines)
  >>> print(names)
  ['name=Plugin One', 'name=Plugin Two']

now replace with exact values.
Try some simple search and replace::

  >>> p = re.compile('name=Plugin One')
  >>> lines = p.sub("name=Plugin One New!", lines)
  >>> print(lines)
  Feature Infobox
  |name=Plugin One New!
  ...

replace new line with empty string::

  >>> p = re.compile('\\n')
  >>> replaced = p.sub('', lines);

replace oneline with replaced::

  >>> onelinesrc = onelinesrc.replace(oneline, replaced)
  >>> print(onelinesrc)
  {{Feature Infobox|name=Plugin One New!...}}
  other content.
