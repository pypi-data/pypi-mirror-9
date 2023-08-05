#!/usr/bin/env python
import os.path
import sys
from glob import glob

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


def get_version():
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path = [src_path] + sys.path
    import disktools
    disktools.__path__
    return disktools.__version__


setup(
    name='disktools',
    version=get_version(),
    description='Extensions to basic disk tools like du, df, etc, but '
                'written in python',
    long_description=readme(),
    author='Yauhen Yakimovich',
    author_email='eugeny.yakimovitch@gmail.com',
    url='https://github.com/ewiger/disktools',
    license='MIT',
    scripts=['bin/duc'],
    # data_files=glob('libexec/*'),
    packages=['disktools'],
    package_dir={'': 'src'},
    download_url='https://github.com/ewiger/disktools/tarball/master',
    install_requires=[
        'argparse >= 1.1',
        'bson >= 0.3.3',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
    ],
)
