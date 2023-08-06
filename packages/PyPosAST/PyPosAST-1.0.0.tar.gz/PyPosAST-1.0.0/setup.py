#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages


print find_packages(exclude=["tests_*", "tests"])

setup(
    name="PyPosAST",
    version="1.0.0",
    description="Extends Python ast nodes with positional informations",
    packages = find_packages(exclude=["tests_*", "tests"]),
    author = ("Joao Pimentel",),
    author_email = "joaofelipenp@gmail.com",
    license = "MIT",
    keywords = "ast python position offset",
    url = "https://github.com/JoaoFelipe/PyPosAST",
)
