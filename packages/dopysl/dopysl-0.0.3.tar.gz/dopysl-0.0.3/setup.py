#!/usr/bin/env python
import dopysl

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(filename):
    return open(filename).read()

setup(
    name="dopysl",
    version=dopysl.__version__,
    description="Digital Ocean PYthon client that Sucks Less",
    long_description=read("README.md"),
    author="Tomas Karasek",
    author_email="tom.to.the.k@gmail.com",
    maintainer="Tomas Karasek",
    maintainer_email="tom.to.the.k@gmail.com",
    url="https://github.com/t0mk/dopysl",
    download_url="https://github.com/t0mk/dopysl/archive/master.zip",
    classifiers=("Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7"),
    license=read("LICENSE"),
    packages=['dopysl'],
    install_requires=["requests >= 1.0.4"],
)
