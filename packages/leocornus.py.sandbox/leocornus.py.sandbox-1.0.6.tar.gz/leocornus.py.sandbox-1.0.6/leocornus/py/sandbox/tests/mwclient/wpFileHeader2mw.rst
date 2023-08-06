Extract WordPress File Header and Save as Wiki Page
===================================================

This story is about extract names and values from `WordPress file
header`_ and save them as a MediaWiki page.

.. contents:: table of contents
   :depth: 5

Set up testing
--------------

Create the testing folder.
All temporary testing files will be stored here.
::

  >>> import os
  >>> from leocornus.py.sandbox.utils_basic import create_file
  >>> from leocornus.py.sandbox.utils_basic import extract_wp_header
  >>> from leocornus.py.sandbox.utils_mwclient import mw_create_page
  >>> from leocornus.py.sandbox.utils_mwclient import mw_replace_page
  >>> from leocornus.py.sandbox.utils_mwclient import mw_page_exists

  >>> homeFolder = os.path.expanduser('~')
  >>> testFolder = os.path.join(homeFolder, 'testmw')
  >>> os.path.exists(testFolder)
  False
  >>> create_file(testFolder, 'readme.txt', '')
  >>> os.path.exists(testFolder)
  True

Important Assumptions
---------------------

- The value for WordPress header field  will be all in one line.

Header to Wiki Template Mapping
-------------------------------

We will use wiki template to save those file header fields.
Here is a list of WordPress file headers we will extract the values:

- Plugin/Theme Name
- Plugin/Theme URI
- Description
- Version

Create a WordPress file headers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a dummy WordPress plugin for testing purpose.
Here is the content of the plugin file::

  >>> data = """/**
  ...  * Plugin Name: Plugin One
  ...  * Plugin URI: http://www.plugin.com
  ...  * Description: plugin description.
  ...  * Version:  1.0.2
  ...  */
  ...  # *comments**
  ... <?php
  ... phpinfo()"""

We will create this file in a plugin folder::

  >>> pluginFolder = os.path.join(testFolder, 'pluginone')
  >>> create_file(pluginFolder, 'one.php', data)

Here is a theme file header.

Here is an example of Wiki template::

  {{Feature Infobox
  |name = BP Group Documents
  |implementation = Document Management for BuddyPress Group, 
  |type = WordPress Network Plugin
  |description = BP Group Documents creates a page ...
  |latest_version = 1.8
  |internet_page = [http://wordpress.org/ Plugin Homepage]
  |download = [https://some.wordpress.org/bpdoc.zip pbdoc.zip]}}
  [[Category:Feature]]

Get ready the data template for the new wiki page.
This is the minimium request for new page.::

  >>> pageTemplate = """{{Feature Infobox
  ... |name=%(name)s
  ... |internet_page=%(internet_page)s
  ... |description=%(description)s
  ... |latest_version=%(latest_version)s
  ... |download=%(download)s}}
  ... """

Here are the mapping.

================== ============================================
Wordpress Header   Wiki Template Field
================== ============================================
Plugin/Theme Name  name, 
                   This will be also the page title.
Plugin/Theme URI   internet_page,
                   This should be Wiki syntax with proper label
Description        description
Version            latest_version
================== ============================================

Other Wiki Template Fields
--------------------------

:download:
  The value for download will be in wiki syntax with the
  the following pattern: 
  **[http://BASE_URL/FILENAME.zip FILENAME.zip]**.
  **FILENAME** will be **FOLDER_NAME.Version**

Processing Scenarios
--------------------

There are 2 main scenarios: create and update.
For creation, it is simple and straitforward.

How to determine?
~~~~~~~~~~~~~~~~~

As we agreed, the name (Plugin Name or Theme Name) will be the 
wiki page title.
So the page is exist or not will be the condition to determine
this is creation or update scenario.

Creation flow
~~~~~~~~~~~~~

Here is the checklist for creation.

- assume page is not exist.
- create new page using package (plugin or theme) name as title.
- ability to set the template name.
- fill out the template according to the mappings.
- ability to set the default values for any template field.
- ability to set the categories.
- save page and logging the result.

Extract WordPress file headers::

  >>> pluginfile = os.path.join(pluginFolder, 'one.php')
  >>> headers = extract_wp_header(pluginfile)
  >>> print(headers['Version'])
  1.0.2
  >>> print(headers['(Plugin|Theme) Name'])
  Plugin One

Preparing the page content::

  >>> homepage = """[%s %s]""" % (headers['(Plugin|Theme) URI'],
  ...                             'Plugin Homepage')
  >>> download = """[%(base)s/%(name)s.zip %(name)s.zip]""" % dict(
  ...   base = 'http://10.1.1.1/repo',
  ...   name = """pluginone.%s""" % headers['Version']
  ... )
  >>> pageTitle = headers['(Plugin|Theme) Name']
  >>> print(pageTitle)
  Plugin One
  >>> values = dict(
  ...   name = pageTitle,
  ...   description = headers['Description'],
  ...   latest_version = headers['Version'],
  ...   internet_page = homepage,
  ...   download = download
  ... )
  >>> pageContent = pageTemplate % values

Save page content to wiki page.
By default we will skip these tests as it depends on a
live MediaWiki site::

  >>> if not mw_page_exists(pageTitle):
  ...     ret = mw_create_page(pageTitle, pageContent)

Update flow
~~~~~~~~~~~

- assume page is exist.
- access page in edit mode.
- replace content with new value according to the mapping
- save page and logging the result.

::

  >>> if mw_page_exists(pageTitle):
  ...    ret = mw_replace_page(pageTitle, values)

Replace strategy:

- replace all new lines (**re.compile('\\n')**) with empty string.
- get template source.
- replace **\|** with **\n|**, this will be the standard 
  format for a wiki template.
- for each new, we perform find the exact value and replace.
- replace new line with empty string for the replaced string.
- replace the template source with the replaced string for the 
  whole page content from first step.

Clean up after testing
----------------------

Simply remove the whole test folder to clean up.
::

  >>> import shutil
  >>> if(os.path.exists(testFolder)):
  ...     shutil.rmtree(testFolder)
  >>> os.path.exists(testFolder)
  False

.. _WordPress file header: https://codex.wordpress.org/File_Header
