#!/usr/bin/env python
from setuptools import setup

short_description = 'Robot Framework Jalali Date'
try:
    description = open('README.rst').read()
except IOError:
    description = short_description


classifiers = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Topic :: Software Development :: Testing
Topic :: Software Development :: Quality Assurance
""".strip().splitlines()

setup(
    name='robotframework-jalali',
    package_dir={'': 'robotframework-jalali'},
    packages=['jalaliLibrary'],  # this must be the same as the name above
    version='0.0.1',
    description=short_description,
    author='samira esnaashari',
    author_email='samir.esnaashari@gmail.com',
    url='https://github.com/samira-esnaashari/robotframework-jalali',
    download_url='https://pypi.python.org/pypi/robotframework-jalali',
    keywords=('robotframework testing '
              'test automation testautomation '
              'atdd bdd jalali'),  # arbitrary keywords
    install_requires=[],
    long_description=description,
    license='MIT',
    classifiers=classifiers,
    platforms='any'
)