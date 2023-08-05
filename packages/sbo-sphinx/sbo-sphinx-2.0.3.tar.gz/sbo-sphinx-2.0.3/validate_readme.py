#!/usr/bin/env python
"""
Determine if a reStructuredText file will display correctly as a package description on PyPI
"""

import argparse
import os
import sys

from sbo_sphinx.pypi_description import processDescription


def validate(args):
    if not os.path.exists(args.path):
        print('No such file: {}'.format(args.path))
        sys.exit(2)

    with open(args.path, 'r') as f:
        source = f.read()

    try:
        result = processDescription(source)
    except Exception as e:
        print('There was a problem parsing the file:\n')
        print(e)
        sys.exit(1)

    print('Successfully parsed the file, PyPI should display it correctly')

    if args.verbose:
        print('\nThe HTML PyPI will probably use to show that file:\n')
        print(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help='path to a reStructuredText file')
    parser.add_argument('-v', '--verbose', help='also show the expected HTML',
                        action='store_true')
    arguments = parser.parse_args()
    validate(arguments)
