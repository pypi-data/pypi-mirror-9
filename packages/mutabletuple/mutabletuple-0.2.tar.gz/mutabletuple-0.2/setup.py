"""Package setup configuration.

To Install package, run:
    >>> python setup.py install

To install package with a symlink, so that changes to the source files will be immediately available, run:
    >>> python setup.py develop

To run the tests:
    >>> python setup.py test

To check documentation consistency (require docutils module):
    >>> python setup.py --long-description | rst2html.py > _output.html
    >>> python -m doctest README.txt

To upload the distribution:
    >>> python setup.py sdist upload
"""

from __future__ import print_function
from setuptools import setup, find_packages

__version__ = '0.2'

setup(
    name='mutabletuple',
    version=__version__,
    description='Similar to namedlist, but with additional features (nested class, recursive merge, etc).',
    long_description=open('README.txt').read() + '\n' + open('CHANGES.txt').read(),
    url='https://github.com/nicolasbessou/mutabletuple',
    include_package_data=True,
    author='Nicolas BESSOU',
    author_email='nicolas.bessou@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=['namedlist'],
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 ],
    test_suite='mutabletuple.tests',
    )
