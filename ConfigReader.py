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
from gettext import gettext as _
import time
import shutil

def print_debug(txt):
    if shared.debug:
        print ( "%s::%s " %(__name__, txt) )



class ConfigReader:
    def __init__(self):
        import shared
        self.filename=shared.tcos_config_file
        self.kernels=[]
        self.base=shared.tcos_config_base
        self.template=None
        self.templates={}
        self.olddata={}
        self.base_template=None
        self.force_settings={}
        self.ignored_widgets=shared.ignored_widgets
        
        # new vars
        self.confdata={}
        self.getkernels()
        self.getusplash()
        
        self.open_file(self.filename)
        
        

    def loadbase(self):
        print_debug("loadbase() ")
        self.add("base.conf")
        #print_debug ("%s"%self.confdata)

    def readtemplate(self, tpl):
        if os.path.basename(tpl) == os.path.basename(shared.tcosconfig_template):
            tpl=shared.tcosconfig_template
        values={}
        f=open(tpl, 'r')
        data=f.readlines()
        f.close()
        for line in data:
            sline=line.strip()
            if sline == "": continue
            if sline.startswith('#'): continue
            if "=" in sline:
                values[sline.split('=')[0]]=sline.split('=')[1].replace('"','')
        return values

    def add(self, tpl):
        self.olddata=self.confdata
        print_debug("add() tpl=%s"%tpl)
        newdata=self.readtemplate(shared.templates_dir + tpl)
        for key in newdata:
            self.confdata[key]=newdata[key]
        

    def loadtemplates(self):
        print_debug("loadtemplates()")
        for tpl in os.listdir(shared.templates_dir):
            print_debug("found tpl %s"%tpl)
            if tpl.startswith("tcos.conf"):
                self.templates[tpl]=self.readtemplate(shared.templates_dir + tpl)
        for tpl in os.listdir( os.path.dirname(shared.tcosconfig_template) ):
            if tpl.endswith(".conf"):
                self.templates[tpl]=self.readtemplate(os.path.dirname(shared.tcosconfig_template) + "/" + tpl )
        print_debug("found templates %s"%self.templates)
        #print_debug("self.vars = %s"%self.vars)
        #print_debug("self.conf = %s"%self.conf)

    def reloadtemplate(self, tpl):
        self.open_file(shared.templates_dir + "base.conf")
        if tpl == os.path.basename(shared.tcosconfig_template):
            self.force_settings=self.readtemplate(shared.tcosconfig_template)
            if self.force_settings.has_key('TCOS_BASED_TEMPLATE'):
                self.add( self.force_settings['TCOS_BASED_TEMPLATE'] )
        else:
            self.force_settings={}
        self.add(tpl)

    def open_file(self, filename):
        try:
            fd=file(filename, 'r')
            print_debug("open_file() filename %s opened "%filename)
            self.data=fd.readlines()
            fd.close()
            for line in self.data:
                if line != '\n':
                    line=line.replace('\n', '')
                    #self.conf.append(line)
                    if "=" in line and not line.startswith('#'):
                        self.confdata[line.strip().split('=')[0]]=line.strip().split('=')[1].replace('"','')
                        if filename == self.filename:
                            self.ignored_widgets.append(line.strip().split('=')[0])
        except Exception, err:
            print ( "Unable to read %s file, error: %s" %(filename, err) )
            import sys
            sys.exit(1)


    
    def getkernels(self):
        # valid kernel >= 2.6.12
        # perpahps we can try to build initrd image instead of initramfs
        # in kernel < 2.6.12, this require a lot of work in gentcos and init scripts
        
        #print_debug ("getkernels() read all vmlinuz in /boot/")
        for _file in os.listdir(shared.chroot + '/boot'):
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
                    #print_debug( "getkernels() VALID kernel %s" %(kernel) )
                    self.kernels.append(kernel)
                else:
                    print_debug( "getkernels() INVALID OLD kernel %s" %(kernel) )
        return

    def getusplash(self):
        self.usplash_themes=[]
        for _file in os.listdir(shared.chroot + "/usr/lib/usplash/"):
            if _file.find("usplash-artwork.so") == -1 and _file.endswith(".so"):
                #print_debug( "getusplash() VALID usplash %s" %(_file) )
                self.usplash_themes.append( [_file, _file.split(".so")[0]] )
                
        shared.TCOS_USPLASH_VALUES = self.usplash_themes


    def getvalue(self, varname):
        if self.confdata.has_key(varname):
            return self.confdata[varname]
        print_debug("get_value() no varname found %s"%varname)
        return

    def getvars(self):
        print_debug("FIXME OBSOLETE")
        return self.confdata.keys()

    def reset(self):
        print_debug("FIXME FIXME reset()")

    def changevalue(self, varname, newvalue):
        if varname == 'TCOS_TEMPLATE':
            print_debug("changevalue() TCOS_TEMPLATE=%s"%newvalue)
            self.base_template=newvalue
        self.confdata[varname]=newvalue

    def savedata(self, changeddata):
        f=open(shared.tcosconfig_template, 'w')
        f.write("# file generated by tcosconfig on %s\n"%time.ctime())
        f.write("TEMPLATE_DESCRIPTION=\"%s\"\n\n" %_("Template generated by tcosconfig") )
        
        if len(self.force_settings) > 0:
            if self.force_settings.has_key('TCOS_BASED_TEMPLATE'):
                f.write("\n# conf based on template\n")
                f.write( "TCOS_BASED_TEMPLATE=%s\n" %(self.force_settings['TCOS_BASED_TEMPLATE'] )  )
            print_debug("savedata() have data from old template")
            f.write("\n# data from old template\n")
            for key in self.force_settings:
                if not key in ['TEMPLATE_DESCRIPTION', 'TCOS_BASED_TEMPLATE']:
                    if key in changeddata:
                        print_debug("saveconfig() oldkey=%s value=%s is in changeddata=%s"%(key, self.force_settings[key], self.confdata[key]))
                        continue
                    print_debug("savedata() old settings var=%s value =%s"%(key, self.force_settings[key]))
                    f.write( "%s=%s\n" %(key, self.force_settings[key] )  )
            f.write("#end of old template data\n\n")

        #if self.base_template and self.base_template != os.path.basename(shared.tcosconfig_template):
        #    print_debug("savedata() have base_template %s"%self.base_template)
        #    f.write("TCOS_BASED_TEMPLATE=%s\n"%self.base_template)
        #else:
        #    print_debug("savedata() %s"%self.base_template)
        #    f.write("TCOS_BASED_TEMPLATE=%s\n"%self.confdata['TCOS_BASED_TEMPLATE'])
        
        for key in changeddata:
            if key == "TCOS_TEMPLATE":
                print_debug("savedata() TCOS_TEMPLATE=%s"%self.confdata[key])
                continue
            f.write( "%s=%s\n" %(key, self.confdata[key] )  )
        
        f.write("\n#end of template\n")
        f.close()
        os.chmod(shared.tcosconfig_template, 600)
        print_debug("file %s saved" %(shared.tcosconfig_template))
        self.setup_chroot()


    def create_tree(self, fname):
        dirs=fname.split('/')[0:-1]
        fullpath="/"
        for d in dirs:
            fullpath+="/" + d
            if not os.path.isdir(fullpath):
                print_debug("create_tree() mkdir %s"%fullpath)
                os.mkdir(fullpath)
        

    def setup_chroot(self):
        if shared.chroot != "/":
            chroot_template=shared.chroot + shared.tcosconfig_template
            print_debug ("setup_chroot() copying %s => %s"%(shared.tcosconfig_template, chroot_template))
            self.create_tree(chroot_template)
            shutil.copy(shared.tcosconfig_template, chroot_template )
            os.chmod(chroot_template, 600)
        else:
            print_debug("setup_chroot() no chroot defined '%s'"%shared.chroot)

    """
    def open_file(self, filename):
        
        print_debug("open_file() reading data from \"%s\"..." %(filename) )
        try:
            fd=file(filename, 'r')
            print_debug("open_file() filename %s opened "%filename)
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
        

    
    def run(self):
        print_debug("run()")
        self.reset()
        self.getvars()
        self.getkernels()
        self.getusplash()

    def reset(self):
        print_debug("reset() reset data...")
        # reset memory data
        self.data=""
        #self.newdata=None
        #self.newdata=[]
        #print_debug("reset() reset self.newdata...")

        self.conf=None
        self.conf=[]
        print_debug("reset() reset self.conf...")

        self.vars=None
        self.vars=[]
        print_debug("reset() reset self.vars...")

        
        if os.path.exists(self.base):
            self.open_file(self.base)
    
    def save_file(self):
        print_debug ( "save_file() Saving data into %s" %(self.filename) )
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
                #print_debug ( "getvars() self.conf=" + self.conf[i] )
                (var,value)=self.conf[i].split("=", 1)
                self.vars.append(var)
                number=number+1
        print_debug("getvars() number of vars %d" %(number) )
        return
    
    
    def getindex(self,varname):
        #print len(self.conf)
        #if varname == None:
        #    return -1
        #print_debug ( "getindex() varname %s" %(varname) )
        for i in range( len(self.conf) ):
            if self.conf[i].find(varname + "=") == 0:
                return i
        return -1

    

    
    def getvalue(self, varname):
        index=self.getindex(varname)
        #print_debug ("getvalue() %s" %(varname))
        if index == -1:
            print_debug ( "getvalue() %s var NOT FOUND" %(varname) )
            return
        else:
            (var,value) = self.conf[index].split("=", 1)
            #print_debug ("getvalue var=%s value=%s" %(var,value))
            return value.replace('"', '')
    

    def getdescription(self, varname):
        # not used....
        index=self.getindex(varname)
        if index == -1:
            print_debug ( "getdescription() %s var NOT FOUND" %(varname) )
            return ""
        else:
            description = self.conf[index -1 ]
            # delete "# "
            return description.replace("# ", "")
    
    def changevalue(self,varname, newvalue):
        print_debug ( "changevalue() varname \"%s\" newvalue \"%s\"" %(varname, newvalue) )
        if varname == None:
            return
        index=self.getindex(varname)
        if index == -1:
            print_debug ( "changevalue() %s NOT FOUND" %(varname) )
            return
        else:
            # need to clean newdata list to generate again
            # bug duplicate vars in tcos.conf resolved
            self.newdata=None
            self.newdata=[]
            print_debug ( "changevalue() reset self.newdata" )
            for line in self.data:
                if line.find(varname+"=") == 0:
                    print_debug ( "########################################################" )
                    print_debug ( "changevalue() %s=\"%s\"" %(varname, newvalue) )
                    print_debug ( "########################################################" )
                    if varname == "TCOS_APPEND":
                        self.newdata.append(varname + "=\"" + newvalue + '\"\n')
                    else:
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
    """

if __name__ == '__main__':
    shared.debug=True
    conf = ConfigReader ()
    print conf.confdata
    conf.add("base.conf")
    print "\n\n"
    print conf.confdata
    
    #print conf.kernels
    #print conf.vars

