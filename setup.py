#!/usr/bin/python
# -*- coding: UTF-8 -*-
#    TcosConfig version __VERSION__
#
# Copyright (c) 2006-2011 Mario Izquierdo <mariodebian@gmail.com>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# This script is inspired by the debian package python-chardet
import os
import glob
from distutils.core import setup
from distutils.command.build import build
from distutils.command.install_data import install_data as install_data


data_files = []

import sys

def get_debian_version():
    f=open('debian/changelog', 'r')
    line=f.readline()
    f.close()
    version=line.split()[1].replace('(','').replace(')','')
    return version

class build_locales(build):
    def run(self):
        os.system("cd po && make")
        build.run(self)

class tcosconfig_install_data(install_data):
    def run(self):
        install_data.run(self)
        
        # parse __VERSION__ with get_debian_version()
        absdir=os.path.abspath( self.install_dir + '/share/tcosconfig' )
        for pyfile in glob.glob( "%s/*.py" %absdir):
            process_version(pyfile)
        
        # rename tcosconfig script
        new=os.path.abspath( self.install_dir + '/bin/tcosconfig' )
        old=new + ".sh"
        os.rename( old, new )
        process_version(new)
        

def process_version(pyfile):
    version=get_debian_version()
    print("sed -i -e 's/__VERSION__/%s/g' %s" %(version, pyfile) )
    os.system("sed -i -e 's/__VERSION__/%s/g' %s" %(version, pyfile) )

for (path, dirs, files) in os.walk("po"):
    if "tcosconfig.mo" in files:
        target = path.replace("po", "share/locale", 1)
        data_files.append((target, [os.path.join(path, "tcosconfig.mo")]))

def get_files(ipath):
    files = []
    for afile in glob.glob('%s/*'%(ipath) ):
        if os.path.isfile(afile):
            files.append(afile)
    return files

def get_py_files():
    files = []
    for afile in glob.glob('./*.py'):
        if os.path.isfile(afile) and "setup" not in afile:
            files.append(afile)
    return files

# images (menus and buttons)
data_files.append(('share/tcosconfig/images', get_files("images") ))

data_files.append(('share/tcosconfig/ui', get_files('ui') ))

# Desktop files
data_files.append( ('share/applications/', ['tcosconfig.desktop']) )

# python files
data_files.append( ('share/tcosconfig/', get_py_files() ) )



setup(name='tcosconfig',
      description = 'Thin Client Image Builder',
      version=get_debian_version(),
      author = 'Mario Izquierdo',
      author_email = 'mariodebian@gmail.com',
      url = 'http://www.tcosproject.org',
      license = 'GPLv2',
      platforms = ['linux'],
      keywords = ['thin client', 'teacher monitor', 'ltsp'],
      scripts=['tcosconfig.sh'],
      cmdclass = {'build': build_locales, 'install_data' : tcosconfig_install_data},
      data_files=data_files
      )

