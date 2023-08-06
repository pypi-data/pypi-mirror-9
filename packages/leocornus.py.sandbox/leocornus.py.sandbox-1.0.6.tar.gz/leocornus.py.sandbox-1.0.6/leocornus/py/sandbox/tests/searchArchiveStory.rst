Search and Archive Story
========================

.. contents:: Table of Contents
   :depth: 5

Purpose
-------

- Search a folder to identify certain patterns of string, such as 
  plugin name, version, extension name, etc.
- Archive the folder based on name and version, the archive name
  will have pattern name-version.zip

Here are list of supported archive types:

- WordPress plugin
- WordPress Theme

Preparing Testing Folder
------------------------

Get ready a test folder.
All testing activities will happen in this folder.
At the end will remove the whole folder as clean up::

  >>> import os
  >>> homeFolder = os.path.expanduser('~')
  >>> testFolder = os.path.join(homeFolder, 'testfolder')
  >>> os.path.isdir(testFolder)
  False
  >>> os.mkdir(testFolder)
  >>> os.path.isdir(testFolder)
  True

General Functions
-----------------

We will define some general functions for re-use.
Here are some ideas:

- function to prepare testing folder and files.
- function to archive a file in zip format.
- utility function to print out some information for verifying.

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

archiveFolder
~~~~~~~~~~~~~

utility function to archive a folder.
There parameters:

:archivePath: the full path the the archive file.
:rootFolder: the parent folder in full path of the source folder
:folderName: the name of the folder in the rootFolder.

Return value: the archive file as a object

Here is the function::

  >>> def archiveFolder(archivePath, rootFolder, folderName):
  ...     # zip the plugin dir
  ...     zip = zipfile.ZipFile(archivePath, "w", 
  ...        compression=zipfile.ZIP_DEFLATED)
  ...     os.chdir(rootFolder)
  ...     for dirpath, dirnames, filenames in os.walk('./' + 
  ...                                                 folderName):
  ...         for name in filenames:
  ...             path = os.path.normpath(os.path.join(dirpath, name))
  ...             if os.path.isfile(path):
  ...                 zip.write(path, path)
  ...     zip.close()
  ...     # need go back to default home foler.
  ...     os.chdir(homeFolder)
  ...     return zip

extractInfo
~~~~~~~~~~~

utility function to extract a set of information from 
the given file full path.

Try to use the basic utility functions module::

  >>> from leocornus.py.sandbox.utils_basic import extract_wp_header
  >>> print(extract_wp_header)
  <function extract_wp_header at ...>

Parameters:

:fullFilePath: the full path to the file.

Return a dict with the following fields:

:fileName: the file name, without path.
:dirName: the full path of the directory.
:folderName: the name of the directory without path.
:packageName: the name of the package, plugin name or theme name
:packageURI: the url to this package.
:version: Version from the file.
:description: the brief description in one line.
:archiveName: the full path to the archive file.

Here are the function::

  >>> def extractInfo(fullFilePath):
  ...     fileName = os.path.basename(fullFilePath)
  ...     #print """File Name: %s""" % fileName
  ...     dirName = os.path.dirname(fullFilePath)
  ...     #print """Dir Name: %s""" % dirName 
  ...     folderName = os.path.basename(dirName)
  ...     #print """Folder Name: %s""" % folderName
  ...     header = extract_wp_header(filepath=fullFilePath, 
  ...                                Version='0.1')
  ...     version = header['Version']
  ...     name = header['(Plugin|Theme) Name']
  ...     description = header['Description']
  ...     uri = header['(Plugin|Theme) URI']
  ...     # get ready the archive name.
  ...     archiveName = """%s.%s.zip""" % (folderName, version)
  ...     #print """Archive Name: %s""" % archiveName
  ...     info = {
  ...       'packageName' : name,
  ...       'packageURI' : uri,
  ...       'description' : description,
  ...       'fileName' : fileName,
  ...       'dirName' : dirName,
  ...       'folderName' : folderName,
  ...       'version' : version,
  ...       'archiveName' : archiveName,
  ...     }
  ...     return info

extractHeader
~~~~~~~~~~~~~

utility function to extract header field from a file.

Params:

:pattern: the grep pattern for the header field.
:fullFilePath: the full path to a file.

Return the value of the header field.
::

  >>> def extractHeader(pattern, fullFilePath):
  ...     # get ready the grep pattern.
  ...     grepPattern = """grep -oE '%s' %s""" % (pattern, fullFilePath)
  ...     try:
  ...         value = subprocess.check_output(grepPattern, shell=True)
  ...         # only split the first one.
  ...         value = value.strip().split(b":", 1)
  ...         return value[1].strip()
  ...     except subprocess.CalledProcessError:
  ...         value = ''

Preparing Testing Files
-----------------------

Here the testing files are for WordPress plugins and themes.
Both of them follow `WordPress file header`_ convensions.
The most important rule is: **one header per line**.

WordPress Plugin
~~~~~~~~~~~~~~~~

The following `WordPress file header`_ identified as 
a WordPress Plugin::

  Plugin Name: name of plugin
  Plugin URI: http://www.website.com/download/url
  Description: one line brief description.
  Version:  2.1.1
  Author: Some name, team name,
  Author URI: http://url.to.author
  Network: true

Here we will get ready some files for testing::

  >>> pluginOne = os.path.join(testFolder, 'pluginone')
  >>> os.mkdir(pluginOne)
  >>> data = """/**
  ...  * Plugin Name: Plugin One
  ...  * Plugin URI: http://www.plugin.com
  ...  * Description: plugin description.
  ...  * Version:  1.0.1
  ...  */
  ...  # *comments**
  ... <?php
  ... phpinfo()"""
  >>> createFile(pluginOne, 'pfileone.php', data)

Add more files here for testing.
Here are files in pluginOne folder::

  >>> createFile(pluginOne, 'pfile2.php', 'some testing code')
  >>> createFile(pluginOne, 'pfile3.php', 'some testing code 3')

Add subfolder css and add some styles::
 
  >>> pluginOneCss = os.path.join(pluginOne, 'css')
  >>> os.mkdir(pluginOneCss)
  >>> createFile(pluginOneCss, 'styles.css', 'styles')
  >>> createFile(pluginOneCss, 'print.css', 'print styles')

WordPress Theme
~~~~~~~~~~~~~~~

The following `WordPress file header`_ in file **style.css** 
identified as a WordPress theme::

  Theme Name: the theme name
  Theme URI: http://theme.com/one
  Description: one line description.
  Version: 3.1.0
  Author: name one,
  Author URI: http://name.one.url

Create testing folders and files for WordPress theme::

  >>> themeOne = os.path.join(testFolder, 'themeone')
  >>> os.mkdir(themeOne)
  >>> os.path.isdir(themeOne)
  True

Create the theme style.css, which tells this is a WordPress theme::

  >>> data = """/**
  ...  * Theme Name: theme one
  ...  * Theme URI: http://www.themeone.com
  ...  * Description: theme description.
  ...  * Version: 2.3
  ...  */
  ... some other infomation **"""
  >>> createFile(themeOne, 'style.css', data)

More files for theme one::

  >>> createFile(themeOne, 'tfileone.php', 'file one php')
  >>> createFile(themeOne, 'tfiletwo.php', 'file two php')
  >>> themeOneImage = os.path.join(themeOne, 'image')
  >>> os.mkdir(themeOneImage)
  >>> createFile(themeOneImage, 'imgone.jpg', 'image one')
  >>> createFile(themeOneImage, 'imgtwo.jpg', 'image two')

Search and Archive
------------------

Search the test folder to find certain string patterns.
The method **os.system** will not return the result.
So we are uing the subprocess module::

  >>> import subprocess
  >>> import zipfile

Grep the testing folder to find eather plugins or themes.
Here are the grep patterns for WordPress plugin and theme::

  $ grep -l 'Plugin Name: ' /full/path/plugins/*/*.php
  $ grep -l 'Theme Name: ' /full/path/themes/*/style.css

We only search one level deep in the testing folder::

  >>> pG = "grep -l 'Plugin Name: ' " + testFolder + "/*/*.php" #**
  >>> plugins = subprocess.check_output(pG, shell=True)
  >>> """Plugin: %s""" % plugins.strip() # doctest: +ELLIPSIS
  'Plugin:...pfileone.php'
  >>> tG = "grep -l 'Theme Name: ' " + testFolder + "/*/style.css"#**
  >>> themes = subprocess.check_output(tG, shell=True)
  >>> print(themes.strip()) # doctest: +ELLIPSIS
  /home/.../themeone/style.css
  >>> allPkgs = plugins + themes
  >>> print allPkgs.strip() # doctest: +ELLIPSIS
  /home/.../pfileone.php
  /home/.../style.css

Archive Plugin
~~~~~~~~~~~~~~

Go through each plugin::

  >>> for plugin in plugins.strip().splitlines():
  ...     # the plugin already has full path, as we grep the 
  ...     # full path pattern.
  ...     info = extractInfo(plugin)
  ...     print("""Package Name: %s""" % info['packageName'])
  ...     print("""Package URI: %s""" % info['packageURI'])
  ...     print("""File Name: %s""" % info['fileName'])
  ...     print("""Plugin Dir: %s""" % info['dirName']) # doctest: +ELLIPSIS
  ...     print("""Plugin Name: %s""" % info['folderName'])
  ...     print("""Version: %s""" % info['version'])
  ...     print("""Archive Name: %s""" % info['archiveName'])
  ...     # archive the plugin.
  ...     # check file exist o not.
  ...     archivePath = os.path.join(testFolder, info['archiveName'])
  ...     os.path.exists(archivePath)
  ...     # zip the plugin dir
  ...     zip = archiveFolder(archivePath, testFolder, 
  ...                         info['folderName'])
  ...     os.path.exists(archivePath)
  ...     files = zip.namelist()
  ...     len(files)
  ...     'pluginone/pfileone.php' in files
  ...     'pluginone/pfile2.php' in files
  ...     'pluginone/pfile3.php' in files
  ...     'pluginone/css/styles.css' in files
  Package Name: Plugin One
  Package URI: http://www.plugin.com
  File Name: pfileone.php
  Plugin Dir: /.../pluginone
  Plugin Name: pluginone
  Version: 1.0.1
  Archive Name: pluginone.1.0.1.zip
  False
  True
  5
  True
  True
  True
  True

Archive Theme
~~~~~~~~~~~~~

Go through each theme::

  >>> for theme in themes.strip().splitlines():
  ...     info = extractInfo(theme)
  ...     print("""Package Name: %s""" % info['packageName'])
  ...     print("""File Name: %s""" % info['fileName'])
  ...     print("""Theme Dir: %s""" % info['dirName']) # doctest: +ELLIPSIS
  ...     print("""Theme Name: %s""" % info['folderName'])
  ...     print("""Version: %s""" % info['version'])
  ...     print("""Archive Name: %s""" % info['archiveName'])
  ...     # archive the Theme.
  ...     archivePath = os.path.join(testFolder, info['archiveName'])
  ...     os.path.exists(archivePath)
  ...     # zip the plugin dir
  ...     zip = archiveFolder(archivePath, testFolder, 
  ...                         info['folderName'])
  ...     os.path.exists(archivePath)
  ...     files = zip.namelist()
  ...     len(files)
  ...     'themeone/style.css' in files
  ...     'themeone/tfileone.php' in files
  ...     'themeone/tfiletwo.php' in files
  ...     'themeone/image/imgone.jpg' in files
  Package Name: theme one
  File Name: style.css
  Theme Dir: /.../themeone
  Theme Name: themeone
  Version: 2.3
  Archive Name: themeone.2.3.zip
  False
  True
  5
  True
  True
  True
  True

Questions TODOs
---------------

The ... seems not working here, might need set up one of the 
option flag::

  Plugin Dir: /home/.../testfolder/pluginone

The **...** works only if you using **print** to show the result and
the testing result is right after the print.

Adding the doctest comment for ELLIPSIS will make sure **...**
work properly.

Remove Testing Folder
---------------------

remove the whole testing folder::

  >>> import shutil
  >>> shutil.rmtree(testFolder)

now verify testFolder is removed::

  >>> os.path.isdir(testFolder)
  False
  >>> os.path.isfile(testFolder)
  False

Doctest Directives
------------------

Here are some interesting doctest directives, more could be found
in post `Basic Python Doctest`_

+ELLIPSIS
  This output will use Ellipsis **...**

+SKIP
  Skip a test.

optionflags
~~~~~~~~~~~

The **optionflags** could be used to set directives for the whole test case.
For examples::

  optionflags = (ELLIPSIS | NORMALIZE_WHITESPACE)
  suite = DocVileSuite(
    'README.rst',
    package = 'leocornus.py.sandbox',
    optionflags = optionflags,
  )

.. _Basic Python Doctest: https://www.packtpub.com/books/content/basic-doctest-python
.. _WordPress file header: https://codex.wordpress.org/File_Header
