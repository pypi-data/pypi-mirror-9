# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup
from distutils.core import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('atxpdf/atxpdf.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "atxpdf",
    packages = ["atxpdf"],
    entry_points = {
        "console_scripts": ['atxpdf = atxpdf.atxpdf:main']
        },
    install_requires = [
        "argh",
        "argcomplete",
        "Pillow"
    ],
    version = version,
    description = "AtExpert PDF generator.",
    long_description = long_descr,
    author = "Frederik Van Leeckwyck",
    author_email = "hogeblekker@hotmail.com",
    url = "http://example.org",
    )
