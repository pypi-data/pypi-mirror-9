# setup.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)
"""DPT API setup script
"""
# There is a Makefile in the DPT distribuion file with multi-language support
# in mind.
#
# This script works directly on the zipped DPT distribution file.
#
# The attempt to use the Mingw32CCompiler class fails in three ways.
# C++ #include statements refer to stdafx.h but the file name is StdAfx.h
# On fixing this by renaming the file, the first few *.cpp files compile but
# bmset.cpp fails at line 53 of du1step.h "error: forward declaration of 'const
# struct dpt::DU1FieldIndex'".  Eight other files fail to compile for the same
# reason.
# It is not clear how to persuade build_ext to use the mingw toolset to do the
# SWIG part of the build.  The nine compilation failures were ignored while
# trying to do this.
#
# No difference attempting to force the command to look like the one used in
# dptMakefile by calls to set_executables().
#
# This setup script does the C++ part of the build by driving the make in
# dptMakefile (the nine modules above are compiled successfully here) and
# then completes the package build using distutils.core.setup.

# The change in status of distutils to legacy prompted some work on switching
# to setuptools, concurrent with upgrade to FreeBSD 10.1 and a portsnap from
# mid-November 2014.  pyNN-setuptoolsNN-5.5.1 was installed as a dependency of
# something so I used that.  NN values are (27 33 34), with 335 being the main
# version for development work.

# With distutils.core.setup(...) 'python3.3 setup.py bdist' succeeds.
# With setuptools.setup(...) 'python3.3 setup.py bdist' fails:
# running build_py
# error: can't copy 'icence.txt': doesn't exist or not a regular file.

# The relevant clauses of setup() call are:
#        package_dir={'dptdb':''},
#        packages=['dptdb'],
#        package_data={'': ['licence.txt', 'LICENCE', '_dptapi.pyd']},

# I had already downloaded the latest version of setuptools to install it on
# Microsoft Windows XP before noticing that the installation had been done for
# me on FreeBSD, so the XP box got setuptools-12.0.5 instead.  January 2015.

# Here setuptools.setup(...) 'python setup.py bdist' fails as well:
# running build_py
# error: can't copy 'icence.txt': doesn't exist or not a regular file.

# The swig command is run as 'wine swig ...' on FreeBSD, but just 'swig ...' on
# Microsoft Windows.  Setup is run as setup(...) function call on Microsoft
# Windows, but as 'wine python _wine_setup.py ...' process call on FreeBSD.

# Reverting to distutils.core.setup(...) gets both commands to succeed.

# Changing directory structure and relevant clauses of setup() call to:
#        include_package_data=True,
#        packages=['dptdb'],
#        package_data={'': ['licence.txt', '_dptapi.pyd']},
# given the setup job is run in a svn checkout directory avoids the problem.

# The Microsoft Windows version of Python 3.4.2 from the msi file includes
# setuptools 2.1 which I found out on installing this Python.  February 2015.

import os
import sys
import subprocess
import zipfile
import shutil
import setuptools
_urllib_available = True
try:
    import urllib.request
except ImportError:
    _urllib_available = False

# Used to check a previously extracted version is the one being extracted.
_EXTRACT = os.path.join('dptdb', 'dptextract')

# Edits to _EXTRACT required for successful build in environment with the
# version of mingw32-g++ used.
_BUILD = os.path.join('dptdb', 'dptbuild')


def setup(
    dpt_distribution_file='DPT_V3R0_DBMS.ZIP',
    dpt_documentation_file='DPT_V3R0_DOCS.ZIP',
    dpt_downloads_from='http://www.solentware.co.uk/files/',
    path_to_swig='C:/swigwin-2.0.8',
    wine_path_to_python='.wine/drive_c',
    **attrs):
    """Extract DPT source code from distribution and call distutils.setup

    dpt_distribution_file is the default DPT distribution
    dpt_documentation_file is the default DPT documentation
    dpt_downloads_from is the site from which DPT files are downloaded
    path_to_swig is the default location of the swig command
    wine_path_to_python is the directory relative to the user's home directory
                        where Python is installed under Wine

    The following command line arguments override these defaults:
    DPT_DIST       dpt_distribution_file
    DPT_DOCS       dpt_documentation_file
    PATH_TO_SWIG   path_to_swig

    PATH_TO_SWIG and path_to_swig are ignored when cross-compiling under *nix.

    The other command line options are described below.

    MINGW345
    gcc-3.4.5 is the most recent version supported by MinGW known to compile
    the DPT API in dpt_distribution_file on Microsoft Windows or Wine without
    any modifications.  The MINGW345 keyword is given on the command line if
    the job should assume mingw32-g++ version 3.4.5 is available.

    When cross-compiling on *nix some changes from '#include "dir\file.h' to
    '#include "dir/file.h' are needed whatever version is available.  Starting
    with an unknown version after MinGW-3.4.5 the header file names <string.h>,
    <limits.h>, and <stdlib.h> must be included, in stdafx.h for convenience,
    to enable successful builds.  MinGW-4.7.2 is known to need this change.

    PATH_TO_PYTHON
    Use this when building under Microsoft Windows if Python is not installed
    directly in the default location.  C:\Python34 for 3.4 versions of Python.
    If the D: drive were used instead then PATH_TO_PYTHON=D:\Python is the
    setting, without the version number which goes in PYTHON_VERSION if needed.

    Python must be installed in wine_path_to_python under Wine.

    PYTHON_VERSION
    Use this when cross-compiling if the build under Wine is to be done for a
    version of Python other than 3.3, the current default.
    PYTHON_VERSION=27 for example, Microsoft Windows version naming convention.

    clean_extract
    Clear out dptapi_python_wrap.cxx, dptapi_python_wrap.o, _dptapi_pyd and
    dptapi.py, generated by SWIG, and the version and licence files, and all
    stuff created from the DPT distribution while doing this.  The files made
    by setuptools.setup() are left alone.

    If present clean_extract is the only command done.

    clean_swig
    Clear out dptapi_python_wrap.cxx, dptapi_python_wrap.o, _dptapi_pyd and
    dptapi.py, generated by SWIG, and the version and licence files.

    If present, and clean_extract is not, clean_swig is the only command done.

    """
    make_arguments = (
        'PATH_TO_PYTHON=',
        'MINGW345',
        'PATH_TO_SWIG=',
        'DPT_DIST=',
        'DPT_DOCS=',
        'PYTHON_VERSION=',
        )

    # In dptMakefile clean_extract should imply clean_swig without it being a
    # pre-requisite relationship.
    clean_up_arguments = ('clean_extract', 'clean_swig')
    
    # Determine the WINE command line option for the 'make' job
    wine = 'WINE=wine'
    if sys.platform == 'win32':
        wine = False

        # The problem here is finding a reliable test to distinguish running
        # under Wine from running under Microsoft Windows.
        # So just state the MSYS requirement for the record.
        sys.stdout.write(
            'On Microsoft Windows this setup must be run in an MSYS shell.\n')
        sys.stdout.write(
            'Otherwise it is assumed the build will be done under Wine.\n')

    if len(sys.argv) < 2:
        sys.stdout.write('Please specify a setup command to setup.py\n')
        return

    # If a clean up argument is present just do the first one found and exit.
    for clean_up in clean_up_arguments:
        for a in sys.argv[1:]:
            if a.lower() == clean_up:

                # GNU make is called gmake in *nix systems but make in msys.
                if sys.platform != 'win32':
                    command = 'gmake'
                else:
                    command = 'make'

                sp = subprocess.Popen(
                    [command, '-f', 'dptMakefile', clean_up], cwd='dptdb')
                
                r = sp.wait()
                if r != 0:
                    sys.stdout.write(
                        ''.join(('dptMakefile ', clean_up, ' command fails\n')))
                else:
                    sys.stdout.write(
                        ''.join(('dptMakefile ', clean_up, ' command done\n')))
                return
    
    for exclude in make_arguments:
        if sys.argv[1].upper().startswith(exclude):
            sys.stdout.write(
                ' '.join((sys.argv[1], 'is not a setup command\n')))
            return
    
    for a in sys.argv[2:]:
        if a.startswith('DPT_DIST='):
            dpt_distribution_file = a.split('=')[-1].strip()
    
    for a in sys.argv[2:]:
        if a.startswith('DPT_DOCS='):
            dpt_documentation_file = a.split('=')[-1].strip()
    
    for a in sys.argv[2:]:
        if a.startswith('PATH_TO_SWIG='):
            path_to_swig = a.split('=')[-1].strip()

    mingw345 = False
    for a in sys.argv[2:]:
        if a.lower() == 'mingw345':
            mingw345 = 'GCC_VERSION_PATCHING=false'

    path_to_python = None
    for a in sys.argv[2:]:
        if a.startswith('PATH_TO_PYTHON='):
            path_to_python = a

    python_version = None
    for a in sys.argv[2:]:
        if a.startswith('PYTHON_VERSION='):
            python_version = a

    downloads = (dpt_distribution_file, dpt_documentation_file)
    if not _urllib_available:
        sys.stdout.write(
            ''.join((
                'Module urllib.request is not in this Python.\n',
                'You will have to download:\n ',
                '\n '.join(downloads),
                '\nmanually if not already present.\n')))
    for distfile in downloads:
        dfile = os.path.join('dptdb', distfile)
        if not os.path.exists(dfile):
            durl = ''.join((dpt_downloads_from, distfile))
            try:
                ddata = urllib.request.urlopen(durl).read()
                dfw = open(dfile, 'wb')
                try:
                    dfw.write(ddata)
                finally:
                    dfw.close()
                sys.stdout.write(' '.join((durl, 'downloaded\n')))
            except:
                sys.stdout.write(
                    ''.join((
                        'Download ',
                        durl,
                        ' failed.\n',
                        'You may have to download this file manually.\n')))
                return

    distfile = os.path.join('dptdb', dpt_distribution_file)
    if not os.path.exists(distfile):
        sys.stdout.write(''.join(('setup cannot find ', distfile, '\n')))
        return
    if not zipfile.is_zipfile(distfile):
        sys.stdout.write(' '.join((distfile, 'is not a zipped file\n')))
        return
    zf = zipfile.ZipFile(distfile)
    ok = False
    try:
        zipbase = os.path.join(_EXTRACT, 'zipcompare')
        present = False
        absent = False
        matched = True
        for n in zf.namelist():
            if os.path.exists(os.path.join(_EXTRACT, n)):
                if os.path.isfile(os.path.join(_EXTRACT, n)):
                    present = True
                    f = open(os.path.join(_EXTRACT, n), 'rb')
                    # 'rb' is not needed on MS Windows Python 3.3.0
                    # 'rb' is needed on Python 3.3.0 built from Python sources
                    # on FreeBSD.
                    # Not known what the FreeBSD port of Python 3.3.n does.
                    # This port is available now, so will find out shortly.
                    try:
                        pft = f.read()
                    finally:
                        f.close()
                    zf.extract(n, path=zipbase)
                    f = open(os.path.join(zipbase, n), 'rb')
                    try:
                        eft = f.read()
                    finally:
                        f.close()
                    del f
                    if eft != pft:
                        sys.stdout.write(' '.join(('file', n, 'changed\n')))
                        matched = False
            else:
                absent = True
            if n == 'licence.txt':
                if os.path.exists(os.path.join(_EXTRACT, n)):
                    if os.path.isfile(os.path.join(_EXTRACT, n)):
                        present = True
                        f = open(os.path.join(_EXTRACT, n), 'rb')
                        try:
                            pft = f.read()
                        finally:
                            f.close()
                        f = open(os.path.join(zipbase, n), 'rb')
                        try:
                            eft = f.read()
                        finally:
                            f.close()
                        del f
                        if eft != pft:
                            sys.stdout.write(' '.join(('file', n, 'changed\n')))
                            matched = False
                else:
                    absent = True
        if present and absent:
            # error
            pass # ok initialised False
        elif absent:
            # extract files
            zf.extractall(path=_EXTRACT)
            zf.extract('licence.txt', path='dptdb') # for ease of redistribution
            ok = True
        elif present:
            ok = matched # all existing files must be unchanged
        if present:
            shutil.rmtree(zipbase)
    finally:
        zf.close()
    if not ok:
        sys.stdout.write(
            ' '.join(('setup abandonned because existing extracted',
                      'files do not match zipped distribution file.\n')))
        return
    
    builddir = os.path.join(os.getcwd(), _BUILD)
    for bd in (
        builddir,
        os.path.join(builddir, 'stdafx'),
        os.path.join(builddir, 'source'),
        os.path.join(builddir, 'include'),
        os.path.join(builddir, 'source', 'dbapi'),
        os.path.join(builddir, 'include', 'dbapi'),
        ):
        try:
            os.mkdir(bd)
        except:
            if not os.path.isdir(bd):
                sys.stdout.write('Create build directory fails\n')
                return
    stdafx_copy = (
        # C++ #include statements refer to stdafx.h
        # dptMakefile references to stdafx.cpp stdafx.h and dptapi_python.i
        # are awkward because of the punctuation characters in the path names.
        (os.path.join(
            _EXTRACT, 'sample projects', 'HelloWorld! (MSVC)', 'StdAfx.h'),
         os.path.join(_EXTRACT, 'stdafx', 'stdafx.h')),
        (os.path.join(
            _EXTRACT, 'sample projects', 'HelloWorld! (MSVC)', 'StdAfx.cpp'),
         os.path.join(_EXTRACT, 'stdafx', 'stdafx.cpp')),
        (os.path.join(
            _EXTRACT, 'sample projects', 'DPT with Python', 'dptapi_python.i'),
         os.path.join(_BUILD, 'dptapi_python.i')),
        )
    for inp, outp in stdafx_copy:
        if os.path.isfile(outp):
            f = open(inp)
            try:
                pft = f.read()
            finally:
                f.close()
            f = open(outp)
            try:
                eft = f.read()
            finally:
                f.close()
            del f
            if eft != pft:
                ok = False
        else:
            f = open(inp)
            try:
                pft = f.read()
                if len(os.path.dirname(outp)):
                    try:
                        os.makedirs(os.path.dirname(outp))#, exist_ok=True)
                    except OSError:
                        pass # assume target directory already exists
                fo = open(outp, 'w')
                try:
                    fo.write(pft)
                finally:
                    fo.close()
                del fo
            finally:
                f.close()
            del f


    def get_source_files(directory):
        """Return list of *.cpp source files without extension.""" 
        files =[]
        for f in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, f)):
                p, e = os.path.splitext(f)
                if e in ('.cpp',):
                    files.append(p)
        return files


    def get_include_files(directory):
        """Return list of *.h source files without extension.""" 
        files =[]
        for f in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, f)):
                p, e = os.path.splitext(f)
                if e in ('.h',):
                    files.append(p)
        return files


    # Use make -f dptMakefile python ... for C++ build of DPT API.
    # The arguments to this wrapper of the setuputils.setup() call allow some
    # flexibility to the build without using command line options.

    # GNU make is called gmake in *nix systems but make in msys.
    if sys.platform != 'win32':
        command = 'gmake'
    else:
        command = 'make'

    job = [
        command,
        '-f',
        '/'.join(os.path.join(
            '..', 'dptMakefile').split('\\')),
        'python']

    job.append(
        ''.join(
            ('DPT_NAMES=',
             ' '.join(get_source_files(
                 os.path.join(_EXTRACT, 'source'))),
             )))
    job.append(
        ''.join(
            ('DPTAPI_NAMES=',
             ' '.join(get_source_files(
                 os.path.join(_EXTRACT, 'source', 'dbapi'))),
             )))

    job.append(
        ''.join(
            ('DPT_INC_NAMES=',
             ' '.join(get_include_files(
                 os.path.join(_EXTRACT, 'include'))),
             )))
    job.append(
        ''.join(
            ('DPTAPI_INC_NAMES=',
             ' '.join(get_include_files(
                 os.path.join(_EXTRACT, 'include', 'dbapi'))),
             )))
    job.append(''.join(('OPTIONS=', '-O3')))
    job.append(''.join(('DEFINES=', '-DNDEBUG')))

    if mingw345:
        job.append(mingw345)
    if wine:
        job.append(wine)
    if path_to_python:
        job.append(path_to_python)
    elif wine:
        job.append(''.join((
            'PATH_TO_PYTHON=',
            os.path.join(
                os.getenv('HOME'),
                wine_path_to_python,
                'Python'))))
        if python_version:
            job.append(python_version)
    else:

        # On Microsoft Windows force make to use the Python version running
        # this job because this job will do the setuptools.setup() call.
        if python_version:
            sys.stdout.write(''.join((
                python_version, ' ignored on Microsoft Windows', '\n')))
        python_version = '='.join((
            'PYTHON_VERSION',
            ''.join([str(vi) for vi in sys.version_info[:2]])))
        job.append(python_version)

    job.append(''.join(('PYTHON_RUNNING_MAKE=', sys.executable)))

    sp = subprocess.Popen(job, cwd=builddir)
    
    r = sp.wait()
    if r != 0:
        sys.stdout.write('Build C++ extension module fails\n')
        return

    version = release = '0'
    dptdb_version = ('0', '0')
    version_file = os.path.join('..', 'version.py')
    for nv in open(os.path.join('dptdb', 'version.py')):
        nv = [v.strip() for v in nv.split('=')]
        if len(nv) == 2:
            n, v = nv
            if n == '_dpt_version':
                v = v[1:-1].split('.')
                if len(v) == 2:
                    version, release = v
            elif n == '_dptdb_version':
                v = v[1:-1].split('.')
                if len(v) in (2, 3):
                    dptdb_version = v

    # Default should be same as PYTHON_VERSION in dptMakefile
    if python_version is None:
        python_version = '33'
    else:
        python_version = python_version.split('=')[-1]
    name = '-'.join((''.join(('dpt', version, '.', release)), 'dptdb'))

    # Remove 'make' arguments from sys.argv before setup() call.
    # Let setup complain if anything is wrong.
    argv = sys.argv[:]
    for e in range(len(sys.argv)-1, 1, -1):
        for exclude in make_arguments:
            if sys.argv[e].upper().startswith(exclude):
                del sys.argv[e]
                break

    if sys.platform == 'win32':
        long_description = open('README.txt').read()
        setuptools.setup(
            name=name,
            version='.'.join(dptdb_version),
            long_description=long_description,
            **attrs)
    else:

        # Do the setup() call in a Wine job.
        job = [
            'wine',
            os.path.join(
                os.getenv('HOME'),
                wine_path_to_python,
                ''.join(('Python', python_version)),
                'python.exe',
                ),
            '_wine_setup.py']
        job.extend(sys.argv[1:])
        job.append(name)
        job.append('.'.join(dptdb_version))
        sp = subprocess.Popen(job)
        
        r = sp.wait()
        if r != 0:
            sys.stdout.write('wine python setup.py ... fails\n')
            return

    sys.argv[:] = argv


if __name__ == '__main__':
    
    setup(
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
