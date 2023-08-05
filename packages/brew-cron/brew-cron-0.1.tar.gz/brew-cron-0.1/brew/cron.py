#!/usr/bin/env python
from . import __version__

import brew
import sys


def main():
    if '--help' in sys.argv:
        print('brew-cron %s:' % __version__)
        print('Options: --fetch --update --upgrade')
        quit()
    if '--update' in sys.argv:
        brew.update()
    outdated = []
    if '--fetch' in sys.argv:
        outdated = brew.outdated()
        brew.fetch(outdated)
    if '--upgrade' in sys.argv:
        brew.upgrade(outdated)


if __name__ == '__main__':
    main()
