#!/usr/bin/python
from setuptools import setup, find_packages

try:
    import multiprocessing  # noqa
except ImportError:
    pass

setup(
    setup_requires=['pbr'],
    pbr=True,
    name="java_role",
    version="0.1",
    packages=find_packages(),
)
