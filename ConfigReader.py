# -*- coding: UTF-8 -*-
##########################################################################
# tcos_config writen by MarioDebian <mariodebian@gmail.com>
#
#    TcosConfig version __VERSION__
#
# Copyright (c) 2005 Mario Izquierdo <mariodebian@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###########################################################################

import os
import shared

def print_debug(txt):
    if shared.debug:
        print ( "DEBUG %s " %(txt) )



class ConfigReader:
    def __init__(self):
        import shared
        self.filename=shared.tcos_config_file
        self.reset()
        self.getvars()
        self.kernels=[]
        self.getkernels()
        self.getusplash()

    def reset(self):
        print_debug("ConfigReader::reset() reset data...")
        # reset memory data
        self.data=""
        #self.newdata=None
        #self.newdata=[]
        #print_debug("ConfigReader::reset() reset self.newdata...")

        self.conf=None
        self.conf=[]
        print_debug("ConfigReader::reset() reset self.conf...")

        self.vars=None
        self.vars=[]
        print_debug("ConfigReader::reset() reset self.vars...")

        self.open_file(self.filename)


    def open_file(self, filename):
        print_debug("ConfigReader::open_file() reading data from \"%s\"..." %(filename) )
	try:
            fd=file(filename, 'r')
            self.data=fd.readlines()
            fd.close()
            for line in self.data:
                if line != '\n':
                    line=line.replace('\n', '')
                    self.conf.append(line)
        except:
            print ( "Unable to read %s file" %(filename) )
            import sys
            sys.exit(1)

    def save_file(self):
        print_debug ( "ConfigReader::save_file() Saving data into %s" %(self.filename) )
        fd=file(self.filename, 'w')
        for line in self.newdata:
            fd.write(line)
        fd.close
        #self.reset()
        #self.getvars()
        return

    def getvars(self):
        #print len(self.conf)
        number=0
        for i in range( len(self.conf) ):
            if self.conf[i].find("#") != 0:
                #print_debug ( "ConfigReader::getvars() self.conf=" + self.conf[i] )
                (var,value)=self.conf[i].split("=", 1)
                self.vars.append(var)
                number=number+1
        print_debug("ConfigReader::getvars() number of vars %d" %(number) )
        return

    def getkernels(self):
        # valid kernel >= 2.6.12
        # perpahps we can try to build initrd image instead of initramfs
        # in kernel < 2.6.12, this require a lot of work in gentcos and init scripts
        
        #print_debug ("ConfigReader::getkernels() read all vmlinuz in /boot/")
        for _file in os.listdir('/boot'):
            # FIXME, in vmlinuz valid names are vmlinuz-X.X.X-extra or vmlinuz-X.X.X_extra
            # if need more string separators add into pattern=re.compile ('[-_]')
            # http://libertonia.escomposlinux.org/story/2006/1/5/223624/2276
            if _file.find('vmlinuz') == 0 :
                kernel=_file.replace('vmlinuz-','')
                # split only 3 times
                (kmay, kmed, kmin) = kernel.split('.',2)
                import re
                pattern = re.compile ('[-_.+]')
                (kmin, kextra) = pattern.split(kmin,1)
                # need kernel >= 2.6.12
                if int(kmay)==2 and int(kmed)==6 and int(kmin)>=12:
                    print_debug( "ConfigReader::getkernels() VALID kernel %s" %(kernel) )
                    self.kernels.append(kernel)
                else:
                    print_debug( "ConfigReader::getkernels() INVALID OLD kernel %s" %(kernel) )
        return

    def getusplash(self):
        self.usplash_themes=[]
        for _file in os.listdir("/usr/lib/usplash/"):
            if _file.find("usplash-artwork.so") == -1:
                print_debug( "ConfigReader::getusplash() VALID usplash %s" %(_file) )
                self.usplash_themes.append( [_file, _file.split(".so")[0]] )
                
        shared.TCOS_USPLASH_VALUES = self.usplash_themes


    def getindex(self,varname):
        #print len(self.conf)
        #if varname == None:
        #    return -1
        #print_debug ( "ConfigReader::getindex() varname %s" %(varname) )
        for i in range( len(self.conf) ):
            if self.conf[i].find(varname) == 0:
                return i
        return -1

    def getvalue(self, varname):
        index=self.getindex(varname)
        #print_debug ("ConfigReader()::get_value() %s" %(varname))
        if index == -1:
            print_debug ( "ConfigReader::getvalue() %s var NOT FOUND" %(varname) )
            return
        else:
            (var,value) = self.conf[index].split("=", 1)
            return value.replace('"', '')

    def getdescription(self, varname):
        # not used....
        index=self.getindex(varname)
        if index == -1:
            print_debug ( "ConfigReader::getdescription() %s var NOT FOUND" %(varname) )
            return ""
        else:
            description = self.conf[index -1 ]
            # delete "# "
            return description.replace("# ", "")

    def changevalue(self,varname, newvalue):
        print_debug ( "ConfigReader::changevalue() varname \"%s\" newvalue \"%s\"" %(varname, newvalue) )
        if varname == None:
            return
        index=self.getindex(varname)
        if index == -1:
            print_debug ( "ConfigReader::changevalue() %s NOT FOUND" %(varname) )
            return
        else:
            # need to clean newdata list to generate again
            # bug duplicate vars in tcos.conf resolved
            self.newdata=None
            self.newdata=[]
            print_debug ( "ConfigReader::changevalue() reset self.newdata" )
            for line in self.data:
                if line.find(varname+"=") == 0:
                    print_debug ( "########################################################" )
                    print_debug ( "ConfigReader::changevalue() %s=\"%s\"" %(varname, newvalue) )
                    print_debug ( "########################################################" )
                    self.newdata.append(varname + "=" + newvalue + '\n')
                else:
                    self.newdata.append(line)
            # save data to file
            self.save_file()
            # reset all loaded data
            self.reset()
            # re read vars
            self.getvars()
            return


if __name__ == '__main__':
    conf = ConfigReader ()
    print conf.kernels
    print conf.vars

