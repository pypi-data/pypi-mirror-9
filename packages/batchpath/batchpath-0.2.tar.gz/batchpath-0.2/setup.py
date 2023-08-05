# -*- coding: utf-8 -*-

from setuptools import setup
from batchpath import __module__
from batchpath import __version__


def read(filename):
    with open(filename) as f:
        return f.read()


setup(
    name=__module__,
    version=__version__,
    author='Brian Beffa',
    author_email='brbsix@gmail.com',
    description="Developer utility to generate and verify pathnames",
    long_description=read('README.rst'),
    url='https://github.com/brbsix/python-batchpath',
    license='GPLv3',
    keywords=['os.walk', 'pathnames', 'paths'],
    py_modules=['batchpath'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
    ],
)
