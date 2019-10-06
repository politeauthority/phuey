#!/usr/bin/env python
"""
Builds packages so that each package can be imported (and allow relative imports)
"""
import setuptools

setuptools.setup(
    name="phuey",
    version="0.0.1",
    author="politeauthority",
    author_email="fullteronalix0@gmail.com",
    url="https://github.com/politeauthority/phuey",
    packages=setuptools.find_packages(),
    scripts=['phuey/bin/phuey'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)