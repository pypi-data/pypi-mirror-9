# _wine_setup.py
# Copyright 2015 Roger Marsh
# Licence: See LICENCE (BSD licence)
"""DPT API setup script for cross-compile builds under Wine.

An interface built with this module will run on Microsoft Windows, but the
purpose of the module is to build the interface for the platform running this
job so the interface can be used on this platform under Wine.

"""
import setuptools
import sys

if __name__ == '__main__':

    # Cannot be sure job is running under Wine, but can rule out non-win32
    # environments.
    if sys.platform != 'win32':
        raise RuntimeError('This job should be run under Wine.')
    
    # Name and version are assumed to have been appended to argv as last two
    # elements by the parent job running under an OS capable of running Wine.
    version = sys.argv.pop()
    name = sys.argv.pop()

    long_description = open('README.txt').read()
    
    setuptools.setup(
        name=name,
        version=version,
        description='DPT database API wrappers built using SWIG',
        author='Roger Marsh',
        author_email='roger.marsh@solentware.co.uk',
        url='http://www.solentware.co.uk',
        packages=[
            'dptdb',
            'dptdb.test',
            ],
        include_package_data=True,
        package_data={
            '': ['licence.txt',
                 '_dptapi.pyd',
                 'DPT_V3R0_DOCS.ZIP',
                 'CONTACT',
                 ],
            },
        platforms='Microsoft Windows',
        long_description=long_description,
        license='BSD',
        classifiers=[
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Operating System :: Microsoft :: Windows',
            'Topic :: Database',
            'Topic :: Software Development',
            'Intended Audience :: Developers',
            'Development Status :: 7 - Inactive',
            ],
        )
