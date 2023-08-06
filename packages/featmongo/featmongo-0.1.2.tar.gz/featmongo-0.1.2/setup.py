#!/usr/bin/env python
import os
import sys
import re

from setuptools import setup
from setuptools.command.test import test as TestCommand


def read_file(filename):
    """Open and a file, read it and return its contents."""
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as f:
        return f.read()


def read_requirements(filename):
    """Open a requirements file and return list of its lines."""
    contents = read_file(filename).strip('\n')
    return contents.split('\n') if contents else []


def extract_dependencies(requirements):
    '''
    Transform any links understood by pip for the format
    accepted by setuptools.
    '''
    result = list()
    matcher = re.compile('https?://.+#egg=([^-]+)-(.+)')
    for index, part in enumerate(list(requirements)):
        match = matcher.search(part)
        if match:
            result.append(part)
            requirements[index] = '%s==%s' % (match.group(1), match.group(2))
    return result


NAME = 'featmongo'
DESCRIPTION = ('Wrapper around pymongo using the serialization '
               'module of feat to convert BSON to python object ')
LONG_DESC = DESCRIPTION
AUTHOR = 'Pragmatic Coders Developers'
AUTHOR_EMAIL = 'dev@pragmaticcoders.com'
LICENSE = "Proprietary"
PLATFORMS = ['any']
REQUIRES = []
SETUP_REQUIRES = ['setuptools>=0.6c9', 'wheel==0.23.0']
INSTALL_REQUIRES = read_requirements('requirements.txt')
TESTS_REQUIRE = read_requirements('requirements_dev.txt')
DEPENDENCY_LINKS = []
DEPENDENCY_LINKS.extend(extract_dependencies(INSTALL_REQUIRES))
DEPENDENCY_LINKS.extend(extract_dependencies(TESTS_REQUIRE))

KEYWORDS = []
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: No Input/Output (Daemon)',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.6',
    ]


PACKAGES = [
    'featmongo',
]

class PyTest(TestCommand):

    """Command to run unit tests after in-place build."""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            'tests',
            'featmongo',
        ]
        self.test_suite = True

    def run_tests(self):
        # Importing here, `cause outside the eggs aren't loaded.
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name = NAME,
      version = '0.1.2',
      description = DESCRIPTION,
      long_description = LONG_DESC,
      # url='',
      author = AUTHOR,
      author_email = AUTHOR_EMAIL,
      license = LICENSE,
      platforms = PLATFORMS,
      setup_requires = SETUP_REQUIRES,
      install_requires = INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      dependency_links=DEPENDENCY_LINKS,
      requires = REQUIRES,
      packages = PACKAGES,
      include_package_data = True,
      keywords = KEYWORDS,
      classifiers = CLASSIFIERS,
      cmdclass={'test': PyTest},
)
