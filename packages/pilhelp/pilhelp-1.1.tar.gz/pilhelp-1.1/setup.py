#!/usr/bin/env python
from distutils.core import setup

from pilhelp import __version__


setup(
    name="pilhelp",
    version=unicode(__version__),
    description="PIL helpers",
    long_description=open("README", 'r').read(),
    author="Fabian Topfstedt",
    author_email="topfstedt@schneevonmorgen.com",
    url="http://bitbucket.org/fabian/pilhelp",
    license="MIT license",
    packages=["pilhelp"],
    install_requires=[
        "Pillow",
    ],
)
