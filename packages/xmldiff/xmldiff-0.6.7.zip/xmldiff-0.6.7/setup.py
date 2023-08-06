#!/usr/bin/env python
from __future__ import nested_scopes
# pylint: disable-msg=W0142, W0403,W0404, W0613,W0622,W0622, W0704, R0904
#
# Copyright (c) 2003 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
""" Generic Setup script, takes package info from __pkginfo__.py file """

__revision__ = '$Id: setup.py,v 1.19 2005/05/03 15:34:36 syt Exp $'

import os
import sys
import shutil
from distutils.core import setup
from os.path import isdir, exists, join, walk

# import required features
from __pkginfo__ import modname, version, license, short_desc, long_desc, \
     web, author, author_email
# import optional features
try:
    from __pkginfo__ import scripts
except:
    scripts = []
try:
    from __pkginfo__ import data_files
except:
    data_files = None
try:
    from __pkginfo__ import subpackage_of
except:
    subpackage_of = None
try:
    from __pkginfo__ import include_dirs
except:
    include_dirs = []
try:
    from __pkginfo__ import ext_modules
except:
    ext_modules = None

BASE_BLACKLIST = ('CVS', 'debian', 'dist', 'build', '__buildlog')
IGNORED_EXTENSIONS = ('.pyc', '.pyo', '.elc')
    

def EnsureScripts(*linuxScripts):
    """
    Creates the proper script names required for each platform
    (taken from 4Suite)
    """
    from distutils import util
    _scripts = linuxScripts
    if util.get_platform()[:3] == 'win':
        _scripts = [s + '.bat' for s in _scripts if exists(s + '.bat')]
    return _scripts


def get_packages(dir, prefix):
    """return a list of subpackages for the given directory
    """
    result = []
    for package in os.listdir(dir):
        absfile = join(dir, package)
        if isdir(absfile):
            if exists(join(absfile, '__init__.py')) or \
                   package in ('test', 'tests'):
                if prefix:
                    result.append('%s.%s' % (prefix, package))
                else:
                    result.append(package)
                result += get_packages(absfile, result[-1])
    return result

def export(from_dir, to_dir,
           blacklist=BASE_BLACKLIST,
           ignore_ext=IGNORED_EXTENSIONS):
    """make a mirror of from_dir in to_dir, omitting directories and files
    listed in the black list
    """
    def make_mirror(arg, dir, fnames):
        """walk handler"""
        for norecurs in blacklist:
            try:
                fnames.remove(norecurs)
            except:
                pass
        for file in fnames:
            # don't include binary files
            if file[-4:] in ignore_ext:
                continue
            if file[-1] == '~':
                continue
            src = '%s/%s' % (dir, file)
            dest = to_dir + src[len(from_dir):]
            print >>sys.stderr, src, '->', dest
            if os.path.isdir(src):
                if not exists(dest):
                    os.mkdir(dest)
            else:
                if exists(dest):
                    os.remove(dest)
                shutil.copy2(src, dest)
    try:
        os.mkdir(to_dir)
    except:
        pass
    walk(from_dir, make_mirror, None)


EMPTY_FILE = '"""generated file, don\'t modify or your data will be lost"""\n'

def install(**kwargs):
    """setup entry point"""
    if subpackage_of:
        package = subpackage_of + '.' + modname
        kwargs['package_dir'] = {package : '.'}
        packages = [package] + get_packages(os.getcwd(), package)
    else:
        kwargs['package_dir'] = {modname : '.'}
        packages = [modname] + get_packages(os.getcwd(), modname)
    kwargs['packages'] = packages
    dist = setup(name = modname,
                 version = version,
                 license =license,
                 description = short_desc,
                 long_description = long_desc,
                 author = author,
                 author_email = author_email,
                 url = web,
                 scripts = EnsureScripts(*scripts),
                 data_files=data_files,
                 ext_modules=ext_modules,
                 **kwargs
                 )
    
    if dist.have_run.get('install_lib'):
        _install = dist.get_command_obj('install_lib')
        if subpackage_of:
            # create Products.__init__.py if needed
            product_init = join(_install.install_dir, subpackage_of,
                                '__init__.py')
            if not exists(product_init):
                f = open(product_init, 'w')
                f.write(EMPTY_FILE)
                f.close()
        
        # manually install included directories if any
        if include_dirs:
            if subpackage_of:
                base = join(subpackage_of, modname)
            else:
                base = modname
            for directory in include_dirs:
                dest = join(_install.install_dir, base, directory)
                export(directory, dest)
    return dist
            
if __name__ == '__main__' :
    install()
