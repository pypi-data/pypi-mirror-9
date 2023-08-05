# dpt_version.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Utility to create version information module for dptdb package.

This script expects to be run in an MSYS shell.

"""

import sys
import os
import re

_DPTDB_VERSION = '0.6.1'


def create_dpt_version_number_module():
    """Extract DPT API version number from parmref.cpp

    This method is adapted from dptversion.py in the DPT API distribution.
    It is not appropriate to share the code between the packages.  In other
    words to amend dptversion.py to cope with this module's needs.

    """
    args = [a.lower() for a in sys.argv]
    args_wine = 'wine' in args
    args_python = 'pythonpackage' in args
    if args_wine and args_python:
        sys.stderr.write(
            'At most one of wine and pythonpackage can be specified')
        return

    for arg in sys.argv:
        if arg.startswith('PYTHON_VERSION='):
            pyversion = arg[len('PYTHON_VERSION='):]
            break
    else:
        pyversion = ''.join(
            (str(sys.version_info[0]), str(sys.version_info[1])))

    version_line = re.compile(''.join((
        '\s*StoreEntry.*VERSDPT.*?(?P<version>((\d+\.)*\d+))')))
    version = '0.0'
    f = open(os.path.join('source', 'parmref.cpp'), 'r')
    for t in f.readlines():
        vl = version_line.match(t)
        if vl is not None:
            version = str(vl.group('version'))
            break
    f.close()

    version = ''.join(('_dpt_version = ', "'", version, "'"))
    dptdb_version = ''.join(('_dptdb_version = ', "'", _DPTDB_VERSION, "'"))
    vft = ''
    version_file = os.path.join('..', 'version.py')
    if os.path.isfile(version_file):
        f = open(version_file)
        try:
            vft = f.read()
        finally:
            f.close()
        if vft != version:
            os.remove(version_file)
    if not os.path.isfile(version_file):
        f = open(version_file, 'w')
        try:
            f.write(version)
            f.write(os.linesep)
            f.write(dptdb_version)
        finally:
            f.close()


if __name__ == '__main__':

    create_dpt_version_number_module()
