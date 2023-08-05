#!/usr/bin/python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import path_overrides

setup(
    name="path_overrides",
    version=path_overrides.__version__,
    author=path_overrides.__author__,
    author_email="benbass@codedstructure.net",
    description="Show executables overriding others with current PATH config",
    long_description=open('README.rst').read(),
    url="http://bitbucket.org/codedstructure/path_overrides",
    py_modules=["path_overrides"],
    scripts=["path_overrides"],
    license="MIT",
    platforms="any",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Utilities",
    ]
)
