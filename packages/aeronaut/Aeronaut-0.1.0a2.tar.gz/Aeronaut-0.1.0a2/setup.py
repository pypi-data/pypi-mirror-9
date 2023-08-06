#! /usr/bin/env python

# Some more useful tips to adopt here http://goo.gl/LbBM3D

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand  # NOQA
import sys


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(name='Aeronaut',
      version='0.1.0a2',
      description='Aeronaut: A client library for DiData Cloud',
      author='Nexus IS Dev Team',
      author_email='dev@nexusis.com',
      packages=find_packages(),
      test_suite='aeronaut.test',
      tests_require=['tox'],
      cmdclass={'test': Tox},
      install_requires=[
          'PyYAML >=3.11',
          'requests >=2.5.1',
          'lxml >=3.4.2'
      ])
