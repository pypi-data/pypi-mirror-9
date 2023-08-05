from setuptools import setup, find_packages

setup(
    name="pip-upgrade",
    version="0.0.6",
    install_requires=['pip >=1.5.1'],
    description="Provides functionality for updating your outdated packages.",
    long_description="""
# Pip Update

## Summary

Updates all outdated packages using pip. Also allows specifying packages,
or showing outdated packages.

## Usage

>    $ pip_upgrade -h
>    usage: Provides functionality for updating all your outdated packages
>
>    positional arguments:
>      PACKAGE_NAME          Name of package to update - without specifying a
>                            package all packages will be updated.
>
>    optional arguments:
>      -h, --help            show this help message and exit
>      -d, --dry, --dry-run  Do not do anything, just print what would be done.

## Authors:

 * Alistair Broomhead
 * Ross Binden

## Contributors

 * Charalampos Papaloizou
 * Frank Herrmann
 * Russel Winder
 * Sam Raza
 * Shivan Sornarajah

## Licence

This code is licence under the [MIT Licence](http://opensource.org/licenses/MIT)
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4"
    ],
    url='https://github.com/alistair-broomhead/pip_upgrade',
    author='pip-upgrade authors',
    keywords='pip',
    license='MIT',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pip_upgrade=pip_upgrade:main"
        ]
    }
)
