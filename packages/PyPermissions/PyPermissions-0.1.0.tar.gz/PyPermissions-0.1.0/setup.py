from setuptools import setup

setup(
    name = "PyPermissions",
    version = "0.1.0",
    author = "Tyler O'Meara",
    author_email = "Tyler@TylerOMeara.com",
    description = "An extensible permissions framework for granular access control.",
    license = "MIT",
    keywords = "permissions access control",
    url = "http://packages.python.org/pypermissions",
    packages = ['pypermissions', 'tests'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)