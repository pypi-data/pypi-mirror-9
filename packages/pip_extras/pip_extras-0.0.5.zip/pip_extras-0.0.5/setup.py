"""
# pip_extras

This is a meta-package for the following:

 - [pip-update](https://pypi.python.org/pypi/pip-upgrade)

The following will be added once a package has been built:

 - [pip-bash-autocomplete](https://github.com/russel/pip_bashcompletion)

Future planned ideas:
"""
from setuptools import setup, find_packages
from sys import argv
import os.path

if "build" in argv:
    DIR_NAME = os.path.dirname(__file__)
    README = os.path.join(DIR_NAME, "README.md")
    open(README, 'w').write(__doc__.strip())

setup(
    name="pip_extras",
    version="0.0.5",
    description="Provides extra pip functionality",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
    ],
    url='https://github.com/russel/pip_extras',
    author='pip_extras authors',
    keywords='pip',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'pip_upgrade >= 0.0.6'
    ]
)