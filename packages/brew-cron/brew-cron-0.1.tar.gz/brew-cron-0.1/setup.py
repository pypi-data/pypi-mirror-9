#!/usr/bin/env python
from setuptools import setup

from brew import __version__

setup(
    name='brew-cron',
    version=__version__,
    description='A helper for Homebrew operations from cron',
    author='Kunal Mehta',
    author_email='legoktm@gmail.com',
    packages=['brew'],
    license='CC-0',
    entry_points={
        'console_scripts': [
            'brew-cron = brew.cron:main'
        ]
    },
    test_suite='tests',
)
