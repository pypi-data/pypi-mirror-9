import os
import re
import sys
from os.path import dirname, join as pjoin
from setuptools import setup, find_packages

with open(pjoin(dirname(__file__), 'orderedmultidict', '__init__.py')) as fd:
    VERSION = re.compile(
        r".*__version__ = '(.*?)'", re.S).match(fd.read()).group(1)

if sys.argv[-1] == 'publish':
    """Publish to PyPi."""
    os.system('python setup.py sdist upload')
    sys.exit()

long_description = ('''
A multivalue dictionary is a dictionary that can store multiple values for the
same key. An ordered multivalue dictionary is a multivalue dictionary that
retains the order of insertions and deletions.

omdict retains method parity with dict.

Information and documentation at https://github.com/gruns/orderedmultidict.''')

required = ['six>=1.8.0']
if sys.version_info < (2, 7):
    required.append('ordereddict')

setup(name='orderedmultidict',
      version=VERSION,
      author='Arthur Grunseid',
      author_email='grunseid@gmail.com',
      url='https://github.com/gruns/orderedmultidict',
      license='Unlicense',
      description='Ordered Multivalue Dictionary - omdict.',
      long_description=long_description,
      packages=find_packages(),
      include_package_data=True,
      platforms=['any'],
      classifiers=['Topic :: Software Development :: Libraries',
                   'Natural Language :: English',
                   'Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: Freely Distributable',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   ],
      install_requires=required,
      test_suite='tests',
      tests_require=[],
      )
