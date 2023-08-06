#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="luigi-td",
    version='0.6.4',
    description="Luigi integration for Treasure Data",
    author="Treasure Data, Inc.",
    author_email="support@treasure-data.com",
    url="https://github.com/treasure-data/luigi-td",
    install_requires=open("requirements.txt").read().splitlines(),
    packages=find_packages(),
    license="Apache License 2.0",
    platforms="Posix; MacOS X; Windows",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
)
