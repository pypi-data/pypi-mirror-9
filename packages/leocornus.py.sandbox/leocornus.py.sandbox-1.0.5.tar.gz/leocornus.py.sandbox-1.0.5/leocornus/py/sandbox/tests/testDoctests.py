# testDoctests.py

from unittest import TestSuite 
from doctest import DocFileSuite
from doctest import ELLIPSIS
from doctest import NORMALIZE_WHITESPACE
# os module.
from os import walk
from os.path import join
from os.path import dirname
from os.path import basename
from os.path import normpath


__author__ = "Sean Chen"
__email__ = "sean.chen@leocorn.com"

optionflags = (ELLIPSIS | NORMALIZE_WHITESPACE)

# set up the testing enviroment.
def setUp(test):
    # nothing for now.
    return

def test_suite():

    suite = TestSuite()

    # add the main README.rst
    suite.addTest(
        DocFileSuite(
            'README.rst',
            package='leocornus.py.sandbox',
            setUp=setUp,
            optionflags=optionflags,
            ),
        )

    # try to walk through current folder to find all rst files
    # and then add them to test suite.
    # This will include all sub folders.
   
    # found out current file's folder.
    testsFolder = dirname(__file__)
    testsFolderName = basename(testsFolder)
    # package folder full path
    pkgFolder = dirname(testsFolder)

    # walk through the current folder, the tests folder.
    for dirpath, dirnames, filenames in walk(testsFolder):
        for name in filenames:
            if name.endswith('.rst'):
                path = normpath(join(dirpath, name))
                # get the relative path to package folder.
                relpath = path.split(pkgFolder)[1][1:]
                # add to test suite.
                suite.addTest(
                    DocFileSuite(
                        relpath,
                        package='leocornus.py.sandbox',
                        setUp=setUp,
                        optionflags=optionflags,
                    ),
                )

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
