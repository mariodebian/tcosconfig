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

import os
import pygtk
pygtk.require('2.0')
import gtk
#from subprocess import Popen, PIPE
from gettext import gettext as _

#from VirtualTerminal import VirtualTerminal 
import shared

from subprocess import Popen, PIPE, STDOUT
from threading import Thread
gtk.gdk.threads_init()

PACKAGE="tcosconfig"
LOCALE_DIR=""

def print_debug(txt):
    if shared.debug:
        print ( "TcosChrootBuilder::%s " %(txt) )

DISTRO_VERSIONS={
"debian":["unstable", "testing", "squeeze"]  ,
"ubuntu":["precise", "oneiric", "natty", "maverick","lucid"],
}



KERNEL_VERSIONS={
"squeeze":"2.6.32-5-486",
"testing":"3.1.0-1-486",
"unstable":"3.1.0-1-486",

"lucid":"2.6.32-37-generic",
"maverick":"2.6.35-31-generic",
"natty":"2.6.38-13-generic",
"oneiric":"3.0.0-14-generic",
"precise":"3.2.0-7-generic",
}

DISTRO_ALIAS={
"stable":"squeeze",
"testing":"wheezy",
"unstable":"sid",
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
        
        self.buildvars={"DISTRIBUTION":"debian", "TCOS_KERNEL":KERNEL_VERSIONS["unstable"]}

        # Widgets
        self.ui = gtk.Builder()
        self.ui.set_translation_domain(shared.PACKAGE)
        print_debug("Loading ui file...")
        self.ui.add_from_file(shared.UI_DIR + 'tcos-chrootbuilder.ui')
        
        self.scrolledwindow = self.ui.get_object("scrolledwindow")
        
        self.window = self.ui.get_object("window")
        self.window.connect("destroy", self.quit )
        
        self.window.set_icon_from_file(shared.IMG_DIR +'tcos-icon.png')
        
        # buttons
        self.button_chroot = self.ui.get_object("button_chroot")
        self.button_delete = self.ui.get_object("button_delete")
        self.button_update = self.ui.get_object("button_update")
        self.button_buildtcos = self.ui.get_object("button_buildtcos")
        self.button_exit = self.ui.get_object("button_exit")
        
        # connect events
        self.button_chroot.connect('clicked', self.buildChroot )
        self.button_delete.connect('clicked', self.deleteChroot )
        self.button_update.connect('clicked', self.updateChroot )
        self.button_buildtcos.connect('clicked', self.buildTcos )
        self.button_exit.connect('clicked', self.quit )
        
        # expander
        self.chroot_options = self.ui.get_object("chroot_options")
        self.chroot_options.set_expanded(False)
        
        
        # widgets
        self.combo_distro = self.ui.get_object("combo_distro")
        self.combo_arch = self.ui.get_object("combo_arch")
        self.entry_kernel = self.ui.get_object("entry_kernel")
        self.entry_mirror = self.ui.get_object("entry_mirror")
        self.combo_distro.connect('changed', self.on_distro_combo_change)

        # new widgets to support forcedistro
        self.combo_distribution = self.ui.get_object("combo_distribution")
        self.combo_distribution.connect('changed', self.on_distribution_combo_change)
        
        self.populate_select(self.combo_distribution, DISTRO_VERSIONS.keys())
        self.populate_select(self.combo_arch, ['i386','amd64'])
        
        # extra mirrors
        self.entry_securitymirror = self.ui.get_object("entry_securitymirror")
        self.entry_tcosmirror = self.ui.get_object("entry_tcosmirror")
        self.ck_experimental = self.ui.get_object("ck_experimental")
        
        self.loadData()
        
        self.entry_tcosmirror.set_text(TCOS_MIRROR)
        self.set_active_in_select(self.combo_distribution, self.buildvars["DISTRIBUTION"] )
        self.set_active_in_select(self.combo_arch, "i386")
        
        if self.buildvars.has_key("TCOS_EXPERIMENTAL") and self.buildvars["TCOS_EXPERIMENTAL"] != "":
            self.ck_experimental.set_active(True)
        
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
        
        #self.term=VirtualTerminal()
        #self.scrolledwindow.add_with_viewport(self.term)
        #self.term.show()
        self.output = self.ui.get_object("output")
        
        
                

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
        version_data=[]
        if os.path.isfile("/var/lib/tcos/version.conf"):
            version_data=self.getFile("/var/lib/tcos/version.conf")

        elif os.path.isfile("/etc/tcos/version.conf"):
            version_data=self.getFile("/etc/tcos/version.conf")

        for line in version_data:
            self.buildvars[line.split("=")[0]]=line.split("=")[1].replace('"','')
        
        tcos_data=self.getFile("/etc/tcos/tcos.conf")
        for line in tcos_data:
            if "TCOS_KERNEL" in line: continue
            if "NEWEST_VMLINUZ" in line: continue
            self.buildvars[line.split("=")[0]]=line.split("=")[1].replace('"','')
        print_debug("loadData() %s" %self.buildvars)
        
        
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
        print_debug ("populate_select() widget=%s => values=%s"%(widget.name, values))
        for value in values:
            print_debug ( "populate_select() appending %s" %([value.split('_')[0]]) ) 
            valuelist.append( [value.split('_')[0]] )
        widget.set_model(valuelist)
        if widget.get_text_column() != 0:
            widget.set_text_column(0)
        #if set_text_column:
        #    widget.set_text_column(0)
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
        tcos_experimental=""
        if self.ck_experimental.get_active():
            tcos_experimental=" --tcos-exp"
        distribution=self.read_select_value(self.combo_distribution, "distribution")
        arch=self.read_select_value(self.combo_arch, "arch")
        version=self.read_select_value(self.combo_distro, "distro")
        if DISTRO_ALIAS.has_key(version):
            version=DISTRO_ALIAS[version]
        cmd=BUILD_CHROOT_CMD + " --create --forcedistro=%s --arch=%s --version=%s --mirror=%s %s --tcosmirror=%s --kversion=%s --dir=%s %s" \
                                        %(distribution, arch, version, mirror, securitymirror_txt, tcosmirror, kversion, self.buildvars["TCOS_CHROOT"], tcos_experimental)
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
        #self.enableButtons()

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
        self.output.set_sensitive(False)
        #self.enableButtons()
        #self.term.fork_command()
        #self.term.run_command(cmd)
        #while 1:
        #    if not self.term.thread_running:
        #        break
        th=Thread(target=self.generateimages, args=(cmd,) )
        th.start()
        
        return

    def generateimages(self, cmdline):
        self.isfinished=False
        p = Popen(cmdline, shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT, close_fds=True)
        print_debug ("generateimages() exec: %s"%cmdline)
        stdout=p.stdout
        counter=0.1
        step=0.02
        while not self.isfinished:
            #time.sleep(0.1)
            line=stdout.readline().replace('\n','')
            
            #if len(line) > 0:
            #    counter=counter+step
                
            if p.poll() != None:
                self.isfinished=True
            
            if 'bash: no job' in line or \
               'root@' in line or \
               'df: Warning' in line:
                print_debug("generateimages() NO VISIBLE LINE %s"%line)
                continue
            
            print_debug("generateimages() %s"%line)
            gtk.gdk.threads_enter()
            self.writeoutputtxt( line )
            gtk.gdk.threads_leave()
        
        gtk.gdk.threads_enter()
        self.enableButtons()
        self.output.set_sensitive(True)
        gtk.gdk.threads_leave()

    def writeoutputtxt(self, txt):
        buffer = self.output.get_buffer()
        iter = buffer.get_end_iter()
        mark = buffer.get_insert()
        txt=str(txt)
        if len(txt) > 80:
            #print_debug("writeoutputtxt() range(len(txt)/80)=%s"%range(len(txt)/70))
            for i in range((len(txt)/80)+1):
                j=i*80
                #print_debug("writeoutputtxt() [%s:%s]" %(j, j+80))
                buffer.insert(iter, '\n' + txt[j:j+80])
        else:
            buffer.insert(iter, '\n' + txt)
        # scroll window
        self.output.scroll_to_mark(mark, 0.2)
        self.output.scroll_to_iter(buffer.get_end_iter(),0.05, True, 0.0, 1.0)
        return

    def run(self):
        gtk.main()
        
    def quit(self, *args):
        gtk.main_quit()
        
if __name__ == "__main__":
    app=TcosChroot()
    app.run()
