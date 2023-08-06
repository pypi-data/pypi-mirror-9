#!/usr/bin/env python

import glob
from setuptools import setup, find_packages

install_requires = []

try:
    import argparse
except ImportError:
    install_requires.append('argparse')

setup(
    name='argcomplete',
    version='0.8.7',
    url='https://github.com/kislyuk/argcomplete',
    license='Apache Software License',
    author='Andrey Kislyuk',
    author_email='kislyuk@gmail.com',
    description='Bash tab completion for argparse',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    packages = find_packages(exclude=['test']),
    scripts = glob.glob('scripts/*'),
    package_data={'argcomplete': ['bash_completion.d/python-argcomplete.sh']},
    zip_safe=False,
    include_package_data=True,
    platforms=['MacOS X', 'Posix'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Shells',
        'Topic :: Terminals'
    ]
)
