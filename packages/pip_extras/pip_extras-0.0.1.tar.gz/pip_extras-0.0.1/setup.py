from setuptools import setup, find_packages

setup(
    name="pip_extras",
    version="0.0.1",
    description="Provides functionality for updating all your outdated packages.",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
    ],
    keywords='pip',
    license='MIT',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pip_update=pip_extras:main",
            ],
        }
    )