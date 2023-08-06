import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as test_command


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


class PyTest(test_command):

    def finalize_options(self):
        test_command.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


version = '0.3'

setup(name='duedil',
      version=version,
      description="Duedil API client",
      long_description=(read('README.rst') + '\n\n' +
                        read('docs', 'HISTORY.rst') + '\n\n' +
                        read('docs', 'TODO.rst')),
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Development Status :: 3 - Alpha', ],
      # Get strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='duedil, api',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='https://github.com/founders4schools/duedil',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      tests_require=['pytest'],
      cmdclass = {'test': PyTest},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
