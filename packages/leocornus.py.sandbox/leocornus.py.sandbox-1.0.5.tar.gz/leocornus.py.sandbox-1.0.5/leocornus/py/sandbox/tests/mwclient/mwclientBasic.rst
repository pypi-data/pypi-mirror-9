Story about mwclient
====================

This is a basic learning story about mwclient_.

.. contents::
   :depth: 5

Query Wikipedia
---------------

This is the basic usage of mwclient_. 
The following testing is mainly based on mwclient_ tutorial.

Try to connect to wikipedia site, the api.php is located at 
path **/w/**. That is also the default path.::

  >>> import mwclient
  >>> site = mwclient.Site('en.wikipedia.org')
  >>> site
  <Site object 'en.wikipedia.org/w/'>

Try to get the **Special:Version** page as a quick test.
The special page should have NO text::

  >>> version = site.Pages['Special:Version']
  >>> version.text()
  u''

Get categories of a page

Get revisions of a page.

Using .mwrc for configuration
-----------------------------

Need os module to access file system.

  >>> import os

Read from ~/.mwrc file. 
The **~/.mwrc** file should have the following format::

  [mwclient]
  host = domain.of.wiki.site
  path = /wiki/
  username = username
  password = password

function hasmwrc()
------------------

create utility function to check if we have .mwrc file.
::

  >>> def getmwinfo():
  ...     homeFolder = os.path.expanduser('~')
  ...     mwrc = os.path.join(homeFolder, '.mwrc')
  ...     mwinfo = {}
  ...     if os.path.exists(mwrc):
  ...         # using ConfigParser module.
  ...         import ConfigParser
  ...         rc = ConfigParser.ConfigParser()
  ...         # read method will return the filename in a list.
  ...         filename = rc.read(mwrc)
  ...         mwinfo['host'] = rc.get('mwclient', 'host')
  ...         mwinfo['path'] = rc.get('mwclient', 'path')
  ...         mwinfo['username'] = rc.get('mwclient', 'username')
  ...         mwinfo['password'] = rc.get('mwclient', 'password')
  ...         # TODO: need check if those values are set properly!
  ...     return mwinfo

Login, Create, and Replace Wiki Page
------------------------------------

Create function to have better control.
::

  >>> def quickCreateReplace():
  ...     mwinfo = getmwinfo()
  ...     # this is how to check if a dict is empty or not.
  ...     if not mwinfo:
  ...         print """<Site object '...'>
  ... Testing Page
  ... Success
  ... True
  ... Success"""
  ...         return # do nothing.
  ...     # we have everything now.
  ...     site = mwclient.Site(mwinfo['host'], path=mwinfo['path'])
  ...     print(site) # doctest: +ELLIPSIS
  ...     site.login(mwinfo['username'], mwinfo['password'])
  ...     testPage = site.Pages['Testing Page']
  ...     text = testPage.edit()
  ...     text = """Tesing page! 
  ... nothing for now
  ... update something again.
  ... maybe something new in the future"""
  ...     text = text + '[[Category: Testing]]'
  ...     ret = testPage.save(text, summary="this is a quick test")
  ...     print(ret['title'])
  ...     print(ret['result'])
  ...     updatePage = site.Pages['Testing Page']
  ...     print(updatePage.exists)
  ...     text = updatePage.edit()
  ...     text = text.replace('[[Category: Testing]]', 
  ...                         '[[Category: My Testing]]')
  ...     ret = updatePage.save(text, summary='Update Category')
  ...     print(ret['result'])

now excute the test::

  >>> quickCreateReplace()
  <Site object '...'>
  Testing Page
  Success
  True
  Success

Q: What's the output if login success?

Q: Does the page create / update by mwclient_ trigger 
`MediaWiki hooks`_?
  mwclient_ using MeidaWiki api.php, which will trigger all hooks.

.. _mwclient: https://github.com/mwclient/mwclient
.. _MediaWiki hooks: http://www.mediawiki.org/wiki/Manual:Hooks
.. _MediaWiki api.php: http://www.mediawiki.org/wiki/Manual:Api.php
