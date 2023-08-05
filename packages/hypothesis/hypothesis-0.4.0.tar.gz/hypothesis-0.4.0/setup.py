from distutils.core import setup
from setuptools.command.test import test as TestCommand
from setuptools import find_packages
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='hypothesis',
    version='0.4.0',
    author='David R. MacIver',
    author_email='david@drmaciver.com',
    packages=find_packages("src"),
    package_dir={"": "src"},
    url='https://github.com/DRMacIver/hypothesis',
    license='MPL v2',
    description='A library for property based testing',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Testing",
    ],
    long_description=open('README.rst').read(),
    tests_require=['pytest', 'pytest-timeout', 'flake8'],
    cmdclass={'test': PyTest},
)
