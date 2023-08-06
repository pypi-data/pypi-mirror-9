# utils_mwclient.py

"""Utility functions to access mwlient_

This will be module __doc__
"""
"""
This is additional docs

Try some testing here:

>>> print(2 * 5)
10

we should be able to the module doc like following:

>>> from leocornus.py.sandbox import utils_mwclient
>>> print(utils_mwclient.__doc__)
Utility functions to access mwlient_
<BLANKLINE>
This will be module __doc__

"""

import os
import re
import mwclient

# Python version 3.0 using all lowercase module name.
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

__author__ = "Sean Chen"
__email__ = "sean.chen@leocorn.com"


# the following functions are rewrite from mwclientBasic.rst

def mw_get_site(mwrc=None):
    """Get MediaWiki site's login info from the given mwrc file.
    The default is ~/.mwrc, if none is specified.

    This function will return a dict objet with the following keys:

    :host: domain name for the MediaWiki site.
    :path: the uri to MediaWiki site.
    :username: MediaWiki site user login.
    :password: MediaWiki site user password.
    """
    """
    Here is a quick test:

    >>> from leocornus.py.sandbox.utils_mwclient import mw_get_site
    >>> print(mw_get_site)
    <function mw_get_site at ...>

    """

    if(mwrc == None):
        # try to get the mw login info from default location:
        # ~/.mwrc 
        home_folder = os.path.expanduser('~')
        mwrc = os.path.join(home_folder, '.mwrc')
    # set the empty dict.
    site = None

    if os.path.exists(mwrc):
        rc = configparser.ConfigParser()
        # the config parser read method will return the filename
        # in a list.
        filename = rc.read(mwrc)
        mwinfo = {}
        mwinfo['host'] = rc.get('mwclient', 'host')
        mwinfo['path'] = rc.get('mwclient', 'path')
        mwinfo['username'] = rc.get('mwclient', 'username')
        mwinfo['password'] = rc.get('mwclient', 'password')
        # TODO: need check if those values are set properly!
        site = mwclient.Site(mwinfo['host'], path=mwinfo['path'])
        site.login(mwinfo['username'], mwinfo['password'])

    return site 

# create a wiki page.
def mw_create_page(title, content):
    """Create a MediaWiki page with the given title and content.
    """

    site = mw_get_site()
    if site == None:
        ret = None
    else:
        thepage = site.Pages[title]
        ret = thepage.save(content, summary="quick test")

    return ret

# check if wiki page exists.
def mw_page_exists(title):
    """Return true if a wiki page with the same title exists.
    """

    site = mw_get_site()
    if site == None:
        return False
    else:
        thepage = site.Pages[title]
        return thepage.exists

# replace a page with new template values.
def mw_replace_page(title, values={}):
    """Replace the page with new values.
    """

    site = mw_get_site()
    if site == None:
        return None
    else:
        thepage = site.Pages[title]
        content = thepage.edit()
        # replace new line with empty string.
        p = re.compile('\\n\|')
        onelineContent = p.sub('|', content)
        # get the template source in one line.
        p = re.compile('{{(.*)}}')
        temps = p.findall(onelineContent)
        oneline = temps[0]
        # replace | to \n as the standard template format.
        p = re.compile('\|')
        lines = p.sub('\\n|', oneline)
        # now for each new value to replace.
        for key, value in values.items():
            p = re.compile("""%s=.*""" % key)
            lines = p.sub("""%s=%s""" % (key, value), lines)
        # make the replaced content in one line too
        p = re.compile('\\n')
        replaced = p.sub('', lines);
        onelineContent = onelineContent.replace(oneline, replaced)
        ret = thepage.save(onelineContent, 'Replace now')
        return ret

