#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


__version__ = "0.0.1"
__author__ = "SkyLothar"
__email__ = "allothar@gmail.com"

__title__ = "docker-registry-driver-ufile"

__url__ = "https://github.com/SkyLothar/docker-registry-driver-ufile"
__description__ = "Docker registry ufile driver"
__download__ = __url__ + "/master.zip"


with open("README.md", "r", "utf-8") as f:
    readme = f.read()

with open("LICENSE", "r", "utf-8") as f:
    license = f.read()

with open("requirements.txt", "r", "utf-8") as f:
    requires = f.read()

with open("tests/requirements.txt", "r", "utf-8") as f:
    tests_requires = f.read()


setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__author__,
    maintainer_email=__email__,
    url=__url__,
    description=__description__,
    long_description=readme,
    download_url=__download__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License"
    ],
    platforms=['Independent'],
    license=license,
    namespace_packages=['docker_registry', 'docker_registry.drivers'],
    packages=['docker_registry', 'docker_registry.drivers'],
    install_requires=requires,
    zip_safe=False,
    tests_require=tests_requires,
    test_suite='nose.collector'
)
