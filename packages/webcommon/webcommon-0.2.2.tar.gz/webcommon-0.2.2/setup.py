"""
Package setup configuration needed for correct package creation
Taken from: https://www.digitalocean.com/community/tutorials/how-to-package-and-distribute-python-applications
"""

from distutils.core import setup

setup(
    # Application name:
    name="webcommon",

    # Version number (initial):
    version="0.2.2",

    # Application author details:
    author="Availab.io",
    author_email="marek@availab.io",

    # Packages
    packages=[
        "webcommon",
        "webcommon.database",
        "webcommon.exceptions",
        "webcommon.json",
        "webcommon.utils",
        "webcommon.logging",
        "webcommon.test"

    ],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://availab.io",

    #
    # license="LICENSE.txt",
    description="Common helper module",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "flask",
        "sqlalchemy",
        "datetime",
        "nose",
        "mock",
        "jsonschema"
    ],
    )