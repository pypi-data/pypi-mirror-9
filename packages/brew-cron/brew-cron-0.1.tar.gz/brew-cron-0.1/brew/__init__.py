#!/usr/bin/env python
__version__ = '0.1'

import subprocess


def update():
    subprocess.check_call(['brew', 'update'])


def outdated():
    out = subprocess.check_output(['brew', 'outdated', '--quiet'])
    return out.decode().strip().splitlines()


def fetch(formulae):
    subprocess.check_call(['brew', 'fetch', '--deps'] + formulae)


def upgrade(formulae):
    subprocess.check_call(['brew', 'upgrade'] + formulae)
