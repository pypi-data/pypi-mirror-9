"""Installs CherryPy using distutils

Run:
    python setup.py install

to install this package.
"""

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import sys
import os
import shutil

required_python_version = '2.3'

###############################################################################
# arguments for the setup command
###############################################################################
name = "CherryPy"
version = "2.3.0"
desc = "Object-Oriented web development framework"
long_desc = "CherryPy is a pythonic, object-oriented web development framework"
classifiers=[
    "Development Status :: 5 - Production/Stable",
    #"Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: Freely Distributable",
    "Programming Language :: Python",
    "Topic :: Internet ",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
]
author="CherryPy Team"
author_email="team@cherrypy.org"
url="http://www.cherrypy.org"
cp_license="BSD"
packages=[
    "cherrypy", "cherrypy.lib", "cherrypy.lib.filter",
    "cherrypy.tutorial", "cherrypy.test", "cherrypy.filters",
]
download_url="http://download.cherrypy.org/cherrypy/2.3.0/"
data_files=[
    ('cherrypy/tutorial',
        [
            'cherrypy/tutorial/tutorial.conf',
            'cherrypy/tutorial/README.txt',
            'cherrypy/tutorial/pdf_file.pdf',
            'cherrypy/tutorial/custom_error.html',
        ]
    ),
    ('cherrypy', ['cherrypy/favicon.ico',]),
    ('cherrypy/test', ['cherrypy/test/style.css',]),
    ('cherrypy/test/static', ['cherrypy/test/static/index.html',
                              'cherrypy/test/static/has space.html',
                              'cherrypy/test/static/dirback.jpg',]),
]
###############################################################################
# end arguments for setup
###############################################################################


def main():
    if sys.version < required_python_version:
        s = "I'm sorry, but %s %s requires Python %s or later."
        print s % (name, version, required_python_version)
        sys.exit(1)
    # set default location for "data_files" to platform specific "site-packages"
    # location
    for scheme in INSTALL_SCHEMES.values():
        scheme['data'] = scheme['purelib']

    dist = setup(
        name=name,
        version=version,
        description=desc,
        long_description=long_desc,
        classifiers=classifiers,
        author=author,
        author_email=author_email,
        url=url,
        license=cp_license,
        packages=packages,
        download_url=download_url,
        data_files=data_files,
    )


if __name__ == "__main__":
    main()
