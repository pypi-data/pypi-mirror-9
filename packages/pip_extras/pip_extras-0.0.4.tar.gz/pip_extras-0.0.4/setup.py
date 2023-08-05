from setuptools import setup, find_packages

setup(
    name="pip_extras",
    version="0.0.4",
    description="Provides functionality for updating all your outdated packages.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
    ],
    url='https://github.com/russel/pip_extras',
    author='Ross Binden & Alistair Broomhead',
    keywords='pip',
    license='MIT',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pip_update=pip_extras:main",
            ],
        }
    )