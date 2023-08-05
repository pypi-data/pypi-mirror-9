# -*- coding utf-8 -*-
#!/usr/bin/env python

# setuptools imports
from setuptools import setup
from setuptools import find_packages

# pybooru imports
import pybooru


with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name="Pybooru",
    version=pybooru.__version__,
    author=pybooru.__author__,
    description="Pybooru is a Python library to access API of Danbooru/Moebooru based sites.",
    long_description=long_description,
    author_email="danielluque14@gmail.com",
    url="https://github.com/LuqueDaniel/pybooru",
    license="MIT License",
    keywords="Pybooru moebooru danbooru API",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet"
        ],
    platforms=['any'],
    install_requires=['requests'],
    packages=find_packages(),
    include_package_data=True,
)
