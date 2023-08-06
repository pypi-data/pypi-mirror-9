import codecs
import os
import re

from setuptools import setup, find_packages

def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'rb', 'utf-8') as f:
        return f.read()

def find_version(*file_paths):
    """
    Build a path from *file_paths* and search for a ``__version__``
    string inside.
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='fhirclient',
    version=find_version("fhirclient/client.py"),
    description='A flexible client for FHIR servers supporting the SMART on FHIR protocol',
    long_description=(read('README.md') + '\n\n' +
                      read('AUTHORS.md')),
    url='https://github.com/smart-on-fhir/client-py/',
    license="APACHE2",
    author="SMART Platforms Team",
    author_email='support@smarthealthit.org',
    packages=find_packages(exclude=['test*']),
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
