#!/usr/bin/env python2.4
# -*- coding: UTF-8 -*-
##########################################################################
# tcos_config writen by MarioDebian <mariodebian@gmail.com>
#
#    TcosConfig version __VERSION__
#
# Copyright (c) 2005 Mario Izquierdo <mariodebian@gmail.com>
# All rights reserved.
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



# debug is false, you can active by tcosconfig --debug
# default config shared class (shared)
# http://mail.python.org/pipermail/tutor/2002-November/018353.html
import shared



def print_debug(txt):
    if shared.debug:
        print txt
    return
    
import sys
import getopt



def usage():
    print "TcosConfig help:"
    print ""
    print "   tcosconfig -d [--debug]  (write debug data to stdout)"
    print "   tcosconfig -h [--help]   (this help)"

    
try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug"])
except getopt.error, msg:
    print msg
    print "for command line options use tcosconfig --help"
    sys.exit(2)


# process options
for o, a in opts:
    if o in ("-d", "--debug"):
        print "DEBUG ACTIVE"
        shared.debug = True
    if o in ("-h", "--help"):
        usage()
        sys.exit()


    
# my own classes
from TcosGui import *



gui = TcosGui()
# Run app
gui.run()

    
