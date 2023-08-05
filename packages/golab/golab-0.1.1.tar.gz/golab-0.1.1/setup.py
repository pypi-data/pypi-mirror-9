#!/usr/bin/env python

from setuptools import setup, find_packages

requirements = []
with open("./requirements.txt") as fp:
    requirements = [l.strip() for l in fp]

setup(
    name="golab",
    version="0.1.1",
    description="Python client for GoLab",
    author="Brett Langdon",
    author_email="brett@blangdon.com",
    url="https://github.com/brettlangdon/golab-python",
    packages=find_packages(),
    license="MIT",
    install_requires=requirements,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ]
)
