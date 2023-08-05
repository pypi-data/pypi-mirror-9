#!/usr/bin/env python
from setuptools import setup

short_description = 'Robot Framework HTTPD Simulator'
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
    name='robotframework-httpd',
    package_dir={'': 'robotframework-httpd'},
    packages=['HTTPDLibrary'],  # this must be the same as the name above
    version='0.5.0',
    description=short_description,
    author='Mohammad Biabani',
    author_email='biabani.mohammad@gmail.com',
    url='https://github.com/mbbn/robotframework-httpd',
    download_url='https://pypi.python.org/pypi/robotframework-httpd',
    keywords=('robotframework testing '
              'test automation testautomation '
              'atdd bdd httpd'),  # arbitrary keywords
    install_requires=['robotframework'],
    long_description=description,
    license='MIT',
    classifiers=classifiers,
    platforms='any'
)