#!/usr/bin/env python
from distutils.core import setup

setup(
    name="testbin",
    version="0.0.6",
    author="Hamza Sheikh",
    author_email="code@codeghar.com",
    url="https://github.com/hamzasheikh/testbin",
    description="Testbin is a library of Python modules and scripts built to help with software testing.",
    license="MIT",
    packages=['testbin', 'testbin.parser'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)

# Additional Resources:
# List of classifiers: https://pypi.python.org/pypi?:action=list_classifiers
# Make installable Python packages: http://gawp.sashahart.net/topics/packaging/
