#!/usr/bin/python

from opcodes import __version__, __author__, __email__
from distutils.core import setup

import os

root_path = os.path.dirname(__file__)

def read_text_file(path):
    with open(os.path.join(root_path, path)) as file:
        return file.read()


setup(
    name="opcodes",
    version=__version__,
    description="Database of Processor Instructions/Opcodes",
    long_description=read_text_file("readme.rst"),
    author=__author__,
    author_email=__email__,
    url="https://github.com/Maratyszcza/Opcodes",
    packages=["opcodes"],
    keywords=["assembly", "assembler", "asm"],
    requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Assembly",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Assemblers",
        "Topic :: Software Development :: Documentation"
    ])
