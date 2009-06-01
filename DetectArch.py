# -*- coding: UTF-8 -*-
##########################################################################
# tcosconfig writen by MarioDebian <mariodebian@gmail.com>
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
import sys
import pygtk
pygtk.require('2.0')
import gtk
from gettext import gettext as _
import shared
from subprocess import Popen, PIPE, STDOUT

class DetectArch:
    def __init__(self):
        self.arch=None
        self.chroot=None
        
    
    def get(self, fakearch=None):
        if fakearch:
            self.arch=fakearch
            return fakearch
        p = Popen("dpkg-architecture", shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT, close_fds=True)
        stdout=p.stdout
        isfinished=False
        while not isfinished:
            line=stdout.readline().strip()
            if p.poll() != None:
                isfinished=True

            if line.find("DEB_BUILD_ARCH=") == 0:
                self.arch=line.split('=')[1].replace('\n','')
                return self.arch


    def buildChroot(self):
        f=open("/etc/tcos/tcos.conf", 'r')
        data=f.readlines()
        f.close()
        for line in data:
            if line.find("TCOS_CHROOT=") == 0:
                self.chroot=line.split("=")[1].replace('\n','')
                break
        #if not os.path.isdir(self.chroot) or not os.path.isdir(self.chroot+ "/usr/bin/"):
        message=_("""Detected non i386 architecture.\n\n
Usually thin clients are i386 machines (Pentium II/II/IV
or AMD K6/K7), you are running %(arch)s architecture.\n\n
Do you want to build a 32bit chroot and generate 32bit TCOS images?\n
If select "No" wizard will construct %(arch)s images.""") %{"arch":self.arch, "arch":self.arch} 
        dialog = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_YES_NO, message_format=message)
        dialog.set_title( _("TcosConfig, invalid architecture") )
        dialog.set_icon ( gtk.gdk.pixbuf_new_from_file(shared.GLADE_DIR + "images/tcos-icon.png") )
        dialog.show_all()
        responce = dialog.run()
        dialog.destroy()
        if responce == -8: # click yes
            from TcosChrootBuilder import TcosChroot
            builder=TcosChroot()
            builder.run()
        else:
            return False
        return True
        

if __name__ == "__main__":
    app=DetectArch()
    print app.get(sys.argv[1])
