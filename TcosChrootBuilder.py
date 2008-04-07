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
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import time
from subprocess import Popen, PIPE
from gettext import gettext as _

from VirtualTerminal import VirtualTerminal 
import shared

PACKAGE="tcosconfig"
LOCALE_DIR=""

def print_debug(txt):
    if shared.debug:
        print ( "TcosChrootBuilder::%s " %(txt) )

DISTRO_VERSIONS={
"debian":["unstable", "testing", "etch"]  ,
"ubuntu":["dapper", "edgy", "feisty", "gutsy", "hardy"]
}



KERNEL_VERSIONS={
"etch":"2.6.18-6-486"  ,
"testing":"2.6.24-1-486"  ,
"unstable":"2.6.23-1-486"  ,
"dapper":"2.6.15-29-386"  ,
"edgy":"2.6.17-12-generic"  ,
"feisty":"2.6.20-16-generic"  ,
"gutsy":"2.6.22-14-generic"  ,
"hardy":"2.6.24-15-generic"
}

DISTRO_ALIAS={
"testing":"lenny"
}

DISTRO_MIRRORS={
"debian":"http://ftp.debian.org/debian"  ,
"ubuntu":"http://archive.ubuntu.com/ubuntu"
}

DISTRO_SEC_MIRRORS={
"debian":"http://security.debian.org/"  ,
"ubuntu":"http://security.ubuntu.com/ubuntu"
}

TCOS_MIRROR="http://www.tcosproject.org"

BUILD_CHROOT_CMD="/usr/sbin/tcos-buildchroot"
#BUILD_CHROOT_CMD="./gentcos"


class TcosChroot:
    def __init__(self):
        
        self.buildvars={}
        
        
        # glade locale init
        gtk.glade.bindtextdomain(shared.PACKAGE, shared.LOCALE_DIR)
        gtk.glade.textdomain(shared.PACKAGE)

        # Widgets
        self.ui = gtk.glade.XML(shared.GLADE_DIR + '/tcos-chrootbuilder.glade')
        
        self.scrolledwindow = self.ui.get_widget("scrolledwindow")
        
        self.window = self.ui.get_widget("window")
        self.window.connect("destroy", self.quit )
        
        # buttons
        self.button_chroot = self.ui.get_widget("button_chroot")
        self.button_delete = self.ui.get_widget("button_delete")
        self.button_update = self.ui.get_widget("button_update")
        self.button_buildtcos = self.ui.get_widget("button_buildtcos")
        self.button_exit = self.ui.get_widget("button_exit")
        
        # connect events
        self.button_chroot.connect('clicked', self.buildChroot )
        self.button_delete.connect('clicked', self.deleteChroot )
        self.button_update.connect('clicked', self.updateChroot )
        self.button_buildtcos.connect('clicked', self.buildTcos )
        self.button_exit.connect('clicked', self.quit )
        
        # expander
        self.chroot_options = self.ui.get_widget("chroot_options")
        self.chroot_options.set_expanded(False)
        
        
        # widgets
        self.combo_distro = self.ui.get_widget("combo_distro")
        self.combo_arch = self.ui.get_widget("combo_arch")
        self.entry_kernel = self.ui.get_widget("entry_kernel")
        self.entry_mirror = self.ui.get_widget("entry_mirror")
        self.combo_distro.connect('changed', self.on_distro_combo_change)

        # new widgets to support forcedistro
        self.combo_distribution = self.ui.get_widget("combo_distribution")
        self.combo_distribution.connect('changed', self.on_distribution_combo_change)
        
        # extra mirrors
        self.entry_securitymirror = self.ui.get_widget("entry_securitymirror")
        self.entry_tcosmirror = self.ui.get_widget("entry_tcosmirror")
        
        self.loadData()
        
        self.entry_tcosmirror.set_text(TCOS_MIRROR)
        self.set_active_in_select(self.combo_distribution, self.buildvars["DISTRIBUTION"] )
        self.set_active_in_select(self.combo_arch, "i386")
        
        if os.path.isfile( os.path.join(self.buildvars["TCOS_CHROOT"], "tcos-buildchroot.conf") ):
            data=[]
            f=open(os.path.join(self.buildvars["TCOS_CHROOT"], "tcos-buildchroot.conf"),'r')
            tmp=f.readlines()
            f.close()
            for cline in tmp:
                line=cline.replace('\n','')
                if line.startswith("DISTRIBUTION="):
                    self.buildvars["DISTRIBUTION"]=line.split('=')[1]
                if line.startswith("MIRROR="):
                    self.entry_mirror.set_text(line.split('=')[1])
                if line.startswith("MIRROR2="):
                    self.entry_securitymirror.set_text(line.split('=')[1])
                if line.startswith("TCOS_MIRROR="):
                    self.entry_tcosmirror.set_text(line.split('=')[1])
                if line.startswith("DISTRIBUTION="):
                    self.set_active_in_select(self.combo_distribution, line.split('=')[1] )
                if line.startswith("TCOS_DISTRO="):
                    distro=self.read_select_value(self.combo_distribution, "distribution")
                    self.populate_select(self.combo_distro, DISTRO_VERSIONS[distro], set_text_column=False)
                    for i in range(len(DISTRO_VERSIONS[distro])):
                        version=line.split('=')[1]
                        for alias in DISTRO_ALIAS:
                            if DISTRO_ALIAS[alias] == line.split('=')[1]:
                                version=alias
                        if DISTRO_VERSIONS[distro][i] == version:
                            self.set_active_in_select(self.combo_distro, DISTRO_VERSIONS[distro][i] )
        
        self.enableButtons()
        
        self.term=VirtualTerminal()
        self.scrolledwindow.add_with_viewport(self.term)
        self.term.show()
        
        
                

    def getFile(self, fname):
        if not os.path.isfile(fname): return []
        data=[]
        f=open(fname, 'r')
        tmp=f.readlines()
        f.close()
        for line in tmp:
            if line.find("#") != 0 and len(line) > 1:
                data.append(line.replace('\n',''))
        return data


    def loadData(self):
        print_debug("loadData() init")
        version_data=self.getFile("/etc/tcos/version.conf")
        for line in version_data:
            self.buildvars[line.split("=")[0]]=line.split("=")[1].replace('"','')
        
        tcos_data=self.getFile("/etc/tcos/tcos.conf")
        for line in tcos_data:
            self.buildvars[line.split("=")[0]]=line.split("=")[1].replace('"','')
        
        
    def on_distro_combo_change(self, widget):
        distro=self.read_select_value(self.combo_distro, "distro")
        if self.buildvars["TCOS_DISTRO"] == distro:
            self.entry_kernel.set_text(self.buildvars["TCOS_KERNEL"])
            print_debug ( "on_distro_combo_change() select default kernel %s" %(self.buildvars["TCOS_KERNEL"]) ) 
        else:
            self.entry_kernel.set_text(KERNEL_VERSIONS[distro])
            print_debug ( "on_distro_combo_change() select kernel %s" %(KERNEL_VERSIONS[distro]) ) 


    def on_distribution_combo_change(self, widget):
        distribution=self.read_select_value(self.combo_distribution, "distribution")
        print_debug ( "on_distribution_combo_change() select distro %s" %(DISTRO_VERSIONS[distribution][-1]) ) 
        self.populate_select(self.combo_distro, DISTRO_VERSIONS[distribution], set_text_column=False)
        self.set_active_in_select(self.combo_distro, DISTRO_VERSIONS[distribution][0] )
        self.entry_mirror.set_text(DISTRO_MIRRORS[distribution])
        self.entry_securitymirror.set_text(DISTRO_SEC_MIRRORS[distribution])

    def populate_select(self, widget, values, set_text_column=True):
        valuelist = gtk.ListStore(str)
        for value in values:
            print_debug ( "populate_select() appending %s" %([value.split('_')[0]]) ) 
            valuelist.append( [value.split('_')[0]] )
        widget.set_model(valuelist)
        if set_text_column:
            widget.set_text_column(0)
        model=widget.get_model()
        return        

    def set_active_in_select(self, widget, default):
        model=widget.get_model()
        for i in range(len(model)):
            #print model[i][0] + default
            if "\"%s\"" %(model[i][0]) == default or model[i][0] == default:
                print_debug ("set_active_in_select(%s) default is %s, index %d"\
                                     %(widget.name, model[i][0] , i ) )
                widget.set_active(i)
                return
        print_debug ( "set_active_in_select(%s) NOT HAVE DEFAULT" %(widget.name) )  
 

    def read_select_value(self, widget, varname):
        selected=-1
        try:
            selected=widget.get_active()
        except:
            print_debug ( "read_select_value() ERROR reading %s" %(varname) )
        model=widget.get_model()
        value=model[selected][0]
        print_debug ( "read_select_value() reading %s=%s" %(varname, value) )
        return value

    def buildChroot(self, *args):
        self.chroot_options.set_expanded(False)
        kversion=self.entry_kernel.get_text()
        mirror=self.entry_mirror.get_text()
        securitymirror=self.entry_securitymirror.get_text()
        if securitymirror != "":
            securitymirror_txt="--securitymirror=%s"%securitymirror
        else:
            securitymirror_txt=""
        tcosmirror=self.entry_tcosmirror.get_text()
        distribution=self.read_select_value(self.combo_distribution, "distribution")
        arch=self.read_select_value(self.combo_arch, "arch")
        version=self.read_select_value(self.combo_distro, "distro")
        if DISTRO_ALIAS.has_key(version):
            version=DISTRO_ALIAS[version]
        cmd=BUILD_CHROOT_CMD + " --create --forcedistro=%s --arch=%s --version=%s --mirror=%s %s --tcosmirror=%s --kversion=%s --dir=%s" \
                                        %(distribution, arch, version, mirror, securitymirror_txt, tcosmirror, kversion, self.buildvars["TCOS_CHROOT"])
        print_debug ("buildChroot() cmd=%s" %cmd) 
        self.run_command(cmd)

    def deleteChroot(self, *args):
        d = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL |
            gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO,
            _("Do you want to delete entire chroot environment?"))
        if d.run() == gtk.RESPONSE_YES:
            print_debug( "deleteChroot response=True" )
            cmd="rm -rf '" + self.buildvars["TCOS_CHROOT"] + "'"
            print_debug("deleteChroot() cmd=%s" %cmd)
            os.system(cmd)
            cmd="rm -rf '" + self.buildvars["TFTP_DIR"] + "/vmlinuz-" + self.buildvars["TCOS_KERNEL"] + "' '" + self.buildvars["TFTP_DIR"] + "/initramfs-" + self.buildvars["TCOS_KERNEL"] + "' '" + self.buildvars["TFTP_DIR"] + "/usr-" + self.buildvars["TCOS_KERNEL"] + ".squashfs' '" + self.buildvars["TFTP_DIR"] + "/linux-" + self.buildvars["TCOS_KERNEL"] + ".nbi'"
            print_debug("deleteChroot() cmd=%s" %cmd)
            os.system(cmd)
        d.destroy()
        self.enableButtons()

    def updateChroot(self, *args):
        self.chroot_options.set_expanded(False)
        kversion=self.entry_kernel.get_text()
        mirror=self.entry_mirror.get_text()
        arch=self.read_select_value(self.combo_arch, "arch")
        version=self.read_select_value(self.combo_distro, "distro")
        cmd=BUILD_CHROOT_CMD + " --update --dir=%s" %(self.buildvars["TCOS_CHROOT"])
        print_debug ("updateChroot() cmd=%s" %cmd) 
        self.run_command(cmd)
        self.enableButtons()

    def buildTcos(self, *args):
        self.chroot_options.set_expanded(False)
        kversion=self.entry_kernel.get_text()
        mirror=self.entry_mirror.get_text()
        arch=self.read_select_value(self.combo_arch, "arch")
        version=self.read_select_value(self.combo_distro, "distro")
        shared.updatetcosimages=True
        shared.chroot=self.buildvars['TCOS_CHROOT']
        shared.tcos_config_file=shared.chroot + "/etc/tcos/tcos.conf"
        shared.gentcos=BUILD_CHROOT_CMD + " --update-images --dir=%s "%(self.buildvars["TCOS_CHROOT"])
        self.window.hide()
        self.quit()


    def disableButtons(self):
        self.button_chroot.set_sensitive(False)
        self.button_delete.set_sensitive(False)
        self.button_update.set_sensitive(False)
        self.button_buildtcos.set_sensitive(False)
        self.button_exit.set_sensitive(False)

    def enableButtons(self):
        if not os.path.isdir(self.buildvars['TCOS_CHROOT']):
            self.button_chroot.set_sensitive(True)
            self.button_delete.set_sensitive(False)
            self.combo_distribution.set_sensitive(True)
            self.combo_distro.set_sensitive(True)
            self.combo_arch.set_sensitive(True)
            self.entry_kernel.set_sensitive(True)
            self.entry_mirror.set_sensitive(True)
            self.entry_securitymirror.set_sensitive(True)
            self.entry_tcosmirror.set_sensitive(True)
            self.chroot_options.set_expanded(True)
        else:
            self.button_chroot.set_sensitive(False)
            self.button_delete.set_sensitive(True)
            self.combo_distro.set_sensitive(False)
            self.combo_distribution.set_sensitive(False)
            self.combo_arch.set_sensitive(False)
            self.entry_kernel.set_sensitive(False)
            self.entry_mirror.set_sensitive(False)
            self.entry_securitymirror.set_sensitive(False)
            self.entry_tcosmirror.set_sensitive(False)
            self.chroot_options.set_expanded(False)
            
        if not os.path.isdir(self.buildvars['TCOS_CHROOT'] + "/boot/"):
            self.button_update.set_sensitive(False)
            self.button_buildtcos.set_sensitive(False)
        else:
            self.button_update.set_sensitive(True)
            self.button_buildtcos.set_sensitive(True)
        self.button_exit.set_sensitive(True)

    def run_command(self, cmd):
        self.disableButtons()
        
        self.term.fork_command()
        self.term.run_command(cmd)
        while 1:
            if not self.term.thread_running:
                break
        """
        message=_("Done")
        dialog = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK, message_format=message)
        dialog.set_title( _("TcosConfig, invalid architecture") )
        dialog.set_icon ( gtk.gdk.pixbuf_new_from_file(shared.GLADE_DIR + "images/tcos-icon.png") )
        dialog.show_all()
        responce = dialog.run()
        dialog.destroy()
        """
        self.enableButtons()
        return
 
    def run(self):
        gtk.main()
        
    def quit(self, *args):
        gtk.main_quit()
        
if __name__ == "__main__":
    app=TcosChroot()
    app.run()
