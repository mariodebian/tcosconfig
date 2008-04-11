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

# Defaults values of TcosConfig

import os
from gettext import gettext as _
from gettext import bindtextdomain, textdomain
from locale import setlocale, LC_ALL

# program name to use in gettext .mo
PACKAGE = "tcosconfig"
VERSION = "__VERSION__"

# constant to font sizes
PANGO_SCALE=1024

# default debug value (overwrite with --debug or -d)
debug=False

# default TCOS config file (default in this path, if installed use global)
tcos_config_file="./tcos.conf"
templates_dir="/usr/share/initramfs-tools-tcos/templates/"

"""
# if exec from svn or sources dir
if os.path.isfile('./tcosconfig.py'):
    LOCALE_DIR = "./po/"
    GLADE_DIR = "./"
    tcos_config_file="./tcos.conf"
    print "TcosConfig not installed, exec in SVN place"
    gentcos="bash gentcos"
else:
    tcos_config_file="/etc/tcos/tcos.conf"
    GLADE_DIR = "/usr/share/tcosconfig/"
    LOCALE_DIR = "/usr/share/locale"
    gentcos="/usr/sbin/gentcos"
"""
# FIXME delete this line and uncomment ^
tcos_config_file="/etc/tcos/tcos.conf"
tcos_config_base=templates_dir + "/base.conf"
GLADE_DIR = "./"
LOCALE_DIR = "./po/"
gentcos="/usr/sbin/gentcos"
#######################################

tcosconfig_template="/etc/tcos/templates/tcosconfig.conf"

# gettext support
setlocale( LC_ALL )
bindtextdomain( PACKAGE, LOCALE_DIR )
textdomain( PACKAGE )

# gentcos command (if svn exec in ./ path else use /usr/sbin/)

chroot="/"
updatetcosimages=False

# Default tcos suffix
tcos_suffix=""

# selectable values and his keys (for tcos.conf file)
# using a bidimensional list
# var_VALUES= [ ['value1','text1'] , ['value2','text2']  ]
# value is saved in tcos.conf
# text can be translatable with _("translatable text")

TCOS_XORG_TYPE_VALUES=[ 
['R', _("Remote XDMCP") ] , 
['L', _("Local X") ], 
['S', _("SSH -X") ] , 
['W', _("rDesktop") ], 
['N', _("Disable") ] 
]

TCOS_XORG_XKB_VALUES=[ 
['us', _("English - us") ] ,
['gb', _("English - gb") ] , 
['es', _("Spanish - es") ], 
['fr', _("French - fr") ] , 
['de', _("German - de") ]
]



TCOS_WEB_BROWSER_VALUES=[
['none', _("Disable") ] ,
['links2', _("Links2 browser") ],
['dillo', _("Dillo browser") ] 
]


TCOS_REMOTEFS_VALUES=[ 
['none', _("Disable")], 
['ltspfs', _("LTSP filesystem") ], 
['shfs', _("SSH filesystem") ] 
]


TCOS_METHOD_VALUES=[ \
['-nbi', _("Eherboot floppy") ], 
['-tftp', _("PXE booting") ],
['-cdrom', _("CDROM booting") ], 
['-nfs -rootfs', _("NFS booting (mem < 38)") ]
]


TCOS_USENFS_VALUES=[ 
['none', _("None") ], 
['nfs', _("Use NFS server") ]
]

TCOS_MENUS_TYPES=[
# text # TCOS_NETBOOT_MENU # TCOS_NETBOOT_MENU_VESA # TCOS_NETBOOT_HIDE_INSTALL
["",            "",                 "", False],
["SIMPLE",      "1",                "", True],
["GRAPHIC",     "1",                "1", True],
]

ignored_widgets=[
'TCOS_NETBOOT_MENU', 
'TCOS_NETBOOT_MENU_VESA',
'TEMPLATE_DESCRIPTION',
'TCOS_BASED_TEMPLATE',
'TEMPLATE_DESCRIPTION_ES',
'TCOS_FORCE_NFS_BUILD']


# widgetname:   [ event   , enable           , disable]

linked_widgets={
'TCOS_X11VNC':['toggled', {'TCOS_XORG':1}, {} ],
'TCOS_FREENX':['toggled', {'TCOS_XORG':1}, {} ],
'TCOS_RDESKTOP':['toggled', {'TCOS_XORG':1}, {} ],
'TCOS_ITALC':['toggled', {'TCOS_XORG':1}, {} ],
# disable some checkboxes when disabling xorg
'TCOS_XORG':['toggled',  {'TCOS_X11VNC':None, 
                         'TCOS_FREENX':None,
                         'TCOS_RDESKTOP':None,
                         'TCOS_ITALC':None,
                         'TCOS_XORG_ALLDRIVERS':None,
                         'TCOS_XORG_OPENGL':None
                         },                {'TCOS_X11VNC':0, 
                                             'TCOS_FREENX':0,
                                             'TCOS_RDESKTOP':0,
                                             'TCOS_ITALC':0,
                                             'TCOS_XORG_ALLDRIVERS':0,
                                             'TCOS_XORG_OPENGL':0}
             ],
'TCOS_SOUND':['toggled', {'TCOS_SOUND_ISA':None, 'TCOS_PULSEAUDIO':None},
                                {'TCOS_SOUND_ISA':0,'TCOS_PULSEAUDIO':0}
             ],
}


