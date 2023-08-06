# encoding: utf-8
from __future__ import absolute_import, print_function

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


__version__ = '0.0.3'
__author__ = 'Dmitry Orlov <me@mosquito.su>'


setup(
    name='topika',
    version=__version__,
    author=__author__,
    author_email='me@mosquito.su',
    license="MIT",
    description="Use pika with tornado with no pain.",
    platforms="all",
    url="http://github.com/mosquito/topika",
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python',
    ],
    install_requires=('pika', 'tornado'),
    long_description=open('README.rst').read(),
    packages=('topika',),
)
