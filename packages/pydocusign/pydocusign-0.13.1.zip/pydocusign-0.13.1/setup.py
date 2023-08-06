#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python packaging."""
import os
import sys

from setuptools import setup


# Tox integration.
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    """Test command that runs tox."""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox  # import here, cause outside the eggs aren't loaded.
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


#: Absolute path to directory containing setup.py file.
here = os.path.abspath(os.path.dirname(__file__))
#: Boolean, ``True`` if environment is running Python version 2.
IS_PYTHON2 = sys.version_info[0] == 2


NAME = 'pydocusign'
DESCRIPTION = 'Python client for DocuSign signature SAAS platform.'
README = open(os.path.join(here, 'README.rst')).read()
VERSION = open(os.path.join(here, 'VERSION')).read().strip()
AUTHOR = u'Benoît Bryon'
EMAIL = 'benoit@marmelune.net'
LICENSE = 'BSD'
URL = 'https://pypi.python.org/pypi/pydocusign/'
CLASSIFIERS = [
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    # Add your classifiers here from
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
]
KEYWORDS = [
    '',
]
PACKAGES = [NAME.replace('-', '_')]
REQUIREMENTS = [
    'beautifulsoup4',
    'certifi',
    'python-dateutil',
    'lxml',
    'pycurl',
    'requests',
    'setuptools',
]
ENTRY_POINTS = {}
TEST_REQUIREMENTS = [
    'tox',
]
if IS_PYTHON2:
    TEST_REQUIREMENTS.extend([
        'mock',
    ])
CMDCLASS = {
    'test': Tox,
}
SETUP_REQUIREMENTS = [
    'setuptools',
]
EXTRA_REQUIREMENTS = {
    'test': TEST_REQUIREMENTS,
    'ssh': ['fabric', 'fabtools'],
}


if __name__ == '__main__':  # Do not run setup() when we import this module.
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=README,
        classifiers=CLASSIFIERS,
        keywords=' '.join(KEYWORDS),
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        license=LICENSE,
        packages=PACKAGES,
        include_package_data=True,
        zip_safe=False,
        install_requires=REQUIREMENTS,
        entry_points=ENTRY_POINTS,
        tests_require=TEST_REQUIREMENTS,
        cmdclass=CMDCLASS,
        setup_requires=SETUP_REQUIREMENTS,
        extras_require=EXTRA_REQUIREMENTS,
    )
