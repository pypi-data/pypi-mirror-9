# istruct - Immutable struct with sane defaults
# Copyright (C) 2015  james sangho nah <sangho.nah@gmail.com>

from setuptools import setup, find_packages

import istruct

setup(
    name="istruct",
    version=istruct.__version__,
    description="Immutable struct with sane defaults",
    long_description=open("README.rst").read(),
    author="james sangho nah",
    author_email="sangho.nah@gmail.com",
    url="https://github.com/microamp/istruct",
    packages=find_packages(),
    package_data={"": ["README.rst", "LICENSE"]},
    include_package_data=True,
    license="MIT",
    zip_safe=True,
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
    )
)
