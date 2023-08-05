#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
try:
    from setuptools import setup, Extension
    from setuptools.command.build_ext import build_ext as _build_ext
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
    from distutils.command.build_ext import build_ext as _build_ext
from urllib import URLopener
from zipfile import ZipFile
import platform
import locale
import struct

PKG_VERSION = '3.0.1'

dir = os.path.abspath(os.path.dirname(__file__))

if '--license-accepted' in sys.argv:
    show_license = False
    sys.argv.remove('--license-accepted')
else:
    show_license = True


class build_ext(_build_ext):
    
    def build_extension(self, ext):
        if ext.language != 'download':
            return _build_ext.build_extension(self, ext)
        
        # Check local dist directory first
        zip_path = os.path.join(dir, 'dist', ext.sources[0].split('/')[-1])
        if not os.path.isfile(zip_path):
            # Download the extension
            print 'Downloading %s extension ...' % ext.name
            sys.stdout.flush() # required to show up in pip
            opener = URLopener()
            try:
                zip_path, headers = opener.retrieve(ext.sources[0])
            except IOError as err:
                errmsg, status, statmsg, headers = err
                if status == 404:
                    sys.exit('Sorry, platform or Python version not supported.')
                raise
        # Get destination path and extension name
        ext_path = self.get_ext_fullpath(ext.name)
        ext_dir, ext_name = os.path.split(ext_path)
        # Get language
        lang = locale.getdefaultlocale()[0] or 'en'
        lang = lang.split('_')[0]
        zip = ZipFile(zip_path)
        try:
            if show_license:
                # Get and show license
                members = zip.namelist()
                for suffix in ('_'+lang, '_en', ''):
                    licensefile = 'license%s.txt' % suffix
                    if licensefile in members:
                        text = zip.read(licensefile).strip()
                        if sys.stdout.encoding:
                            text = text.decode('utf-8')
                            text = text.encode(sys.stdout.encoding)
                        print '\n', '*' * 76, '\n'
                        print text
                        print '\n', '*' * 76, '\n'
                        print 'Do you accept the license? [y/N]: '
                        sys.stdout.flush() # required to show up in pip
                        accepted = raw_input('').strip()
                        if accepted.lower() not in ('y', 'ye', 'yes'):
                            sys.exit('Aborted')
                        break
            # Finally extract the extension
            zip.extract(ext_name, ext_dir)
        finally:
            zip.close()


# Read package description
with open(os.path.join(dir, 'README.txt')) as fh:
    readme = fh.read()

# fintech extension to download
extension = Extension('fintech', sources=[
    'http://www.joonis.de/pyfintech/v%s/fintech-%s-py%s-%s-%sbit.zip' % (
        PKG_VERSION,
        PKG_VERSION,
        '%i.%i' % sys.version_info[:2],
        platform.system().lower(),
        struct.calcsize('P') * 8,
    )], language='download')

setup(
    name='fintech',
    version=PKG_VERSION,
    author='Thimo Kraemer',
    author_email='thimo.kraemer@joonis.de',
    url='http://www.joonis.de/software/fintech',
    description='The Python FinTech package (SEPA, EBICS & more)',
    long_description=readme,
    keywords=('fintech', 'ebics', 'sepa'),
    license='Proprietary, see http://www.joonis.de/software/fintech/license',
    cmdclass={'build_ext': build_ext},
    ext_modules=[extension],
    install_requires=['PyCrypto', 'lxml', 'kontocheck>=5.5.4', 'certifi', 'fpdf'],
    zip_safe=False,
)
