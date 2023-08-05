#!/usr/bin/env python
"""Installs vcs2eric using distutils/setuptools

Run:

    python setup.py install

to install the package from the source archive.
"""
import os
try:
    from setuptools import setup
except ImportError as err:
    from distutils.core import setup

version = [
    (line.split('=')[1]).strip().strip('"').strip("'")
    for line in open(os.path.join('vcs2eric','__init__.py'))
    if line.startswith( '__version__' )
][0]

if __name__ == "__main__":
    extraArguments = {
        'classifiers': [
            """Programming Language :: Python :: 2""",
            """Programming Language :: Python :: 3""",
            """Topic :: Software Development :: Libraries :: Python Modules""",
            """Intended Audience :: Developers""",
        ],
        'keywords': 'vcs,bzr,cvs,svn,git,hg,eric4',
        'platforms': ['Linux'],
    }
    ### Now the actual set up call
    setup (
        name = "vcs2eric",
        version = version,
        url = "https://launchpad.net/vcs2eric",
        download_url = "https://launchpad.net/vcs2eric/+download",
        description = "Generates Eric4 IDE project files from existing VCS checkouts",
        author = "Mike C. Fletcher",
        author_email = "mcfletch@vrplumber.com",
        license = "GPLv3",
        package_dir = {
            'vcs2eric':'vcs2eric',
        },
        packages = [
            'vcs2eric',
        ],
        options = {
            'sdist':{'force_manifest':1,'formats':['gztar','zip'],},
        },
        zip_safe=False,
        entry_points = {
            'gui_scripts': [
                'vcs2eric=vcs2eric.vcs2eric:main',
            ],
        },
        **extraArguments
    )

