#!/usr/bin/env python
from os.path import dirname, abspath, join
from setuptools import setup

here = abspath(dirname(__file__))
readme = open(join(here, "README.rst"))

setup(
    name="mongoengine-mls",
    version="1.0.3",
    py_modules=["mongoengine_mls"],
    url="https://github.com/rembish/mongoengine-mls",
    license="BSD",
    author="Aleksey Rembish",
    author_email="alex@rembish.org",
    description="MultiLingualField for MongoEngine",
    long_description="".join(readme.readlines()),
    install_requires=["mongoengine", "mls"]
)
