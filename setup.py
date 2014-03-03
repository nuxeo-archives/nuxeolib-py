#!/usr/bin/env python

"""A small Python client for the Nuxeo Document Automation JSON-RPC API.

See: https://doc.nuxeo.com/display/NXDOC/Content+Automation for more
information about content automation.
"""

import setuptools

VERSION = "0.2"

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Unix',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


def main():
    setuptools.setup(
        name = "nuxeo-automation",
        license = "LGPL",
        version = VERSION,
        platforms = ["any"],
        py_modules = ["nuxeolib"],
        test_suite = "test",
        author = "Stefane Fermigier",
        author_email = "sf@nuxeo.com",
        description = __doc__.split("\n", 1)[0],
        long_description = __doc__.split("\n", 2)[-1],
        url = "http://",
        download_url = "http://bitbucket.org/sfermigier/nuxeo-automation-clients/downloads",
        classifiers = CLASSIFIERS,
    )

if __name__ == "__main__":
    main()
