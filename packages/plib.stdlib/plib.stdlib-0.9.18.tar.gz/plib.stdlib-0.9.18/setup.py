#!/usr/bin/python -u
"""
Setup script for PLIB.STDLIB package
Copyright (C) 2008-2014 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.stdlib import __version__ as version

name = "plib.stdlib"
description = "Useful packages and modules to extend the Python standard library."

author = "Peter A. Donis"
author_email = "peterdonis@alum.mit.edu"

startline = 5
endspec = "The Zen of PLIB"

dev_status = "Beta"

license = "GPLv2"

ext_names = [
    'plib.stdlib.extensions._extensions',
    'plib.test.stdlib._extensions_testmod'
]
ext_srcdir = "src"

data_dirs = ["examples"]

classifiers = """
Environment :: Console
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Intended Audience :: Developers
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python :: 2.7
Topic :: Software Development :: Libraries :: Python Modules
"""

post_install = ["plib-setup-{}".format(s) for s in ("stdlib-examples",)]

rst_header_template = """**{basename}** for {name} {version}

:Author:        {author}
:Release Date:  {releasedate}
"""


if __name__ == '__main__':
    import sys
    import os
    from subprocess import call
    from distutils.core import setup
    from setuputils import convert_rst, current_date, setup_vars
    
    convert_rst(rst_header_template,
        startline=2,
        name=name.upper(),
        version=version,
        author=author,
        releasedate=current_date("%d %b %Y")
    )
    call(['sed', '-i', 's/bitbucket.org\/pdonis\/plib-/pypi.python.org\/pypi\/plib./', 'README'])
    call(['sed', '-i', 's/bitbucket.org\/pdonis\/plib3-/pypi.python.org\/pypi\/plib3./', 'README'])
    call(['sed', '-i', 's/github.com\/pdonis/pypi.python.org\/pypi/', 'README'])
    setup(**setup_vars(globals()))
    if "install" in sys.argv:
        for scriptname in post_install:
            os.system(scriptname)
