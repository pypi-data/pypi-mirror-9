# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import os.path
import codecs


def read_me():
    with codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        return f.read()

from mac_address_switcher.version import VERSION

setup(
    name='mswitcher',
    packages=['mac_address_switcher'],
    data_files=[('', ['README.rst'])],
    version=VERSION,
    description='Mac address switcher',
    long_description=read_me(),
    license='No license',
    author='Jaeyoung Lee',
    author_email='jaeyoung' + '@monodiary.net',
    maintainer='Jaeyoung Lee',
    maintainer_email='jaeyoung' + '@monodiary.net',
    url='https://github.com/jeyraof/mac-address-switcher',
    entry_points={
        'console_scripts': [
            'mswitcher = mac_address_switcher:switch',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
)
