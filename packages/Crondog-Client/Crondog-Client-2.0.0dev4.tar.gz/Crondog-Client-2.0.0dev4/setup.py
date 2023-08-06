# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search('^__VERSION__\s*=\s*"(.*)"', open('crondogclient/crondog.py').read(), re.M).group(1)


setup(
    name="Crondog-Client",
    packages=["crondogclient"],
    entry_points={
        "console_scripts": ['crondog=crondogclient.crondog:main']
        },
    install_requires=['argparse'],
    version = version,
    description="Python command line client for crondog.",
    author="Craig Pearson",
    author_email="admin@hauntdigital.co.nz",
    url="http://hauntdigital.co.nz",
    )
