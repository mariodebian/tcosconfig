# -*- coding: UTF-8 -*-
##########################################################################
# tcos_config writen by MarioDebian <mariodebian@gmail.com>
#
#    tcos_config version 0.1
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

# Defaults values of TcosConfig

import os
from gettext import gettext as _
from gettext import bindtextdomain, textdomain
from locale import setlocale, LC_ALL

# program name to use in gettext .mo
PACKAGE = "tcosconfig"

# constant to font sizes
PANGO_SCALE=1024

# default debug value (overwrite with --debug or -d)
debug=False

# default TCOS config file (default in this path, if installed use global)
tcos_config_file="./tcos.conf"

# if exec from svn or sources dir
if os.path.isfile('./tcosconfig.py'):
    LOCALE_DIR = "./po/"
    GLADE_DIR = "./"
    tcos_config_file="./tcos.conf"
    print "TcosConfig not installed, exec in SVN place"
else:
    tcos_config_file="/etc/tcos/tcos.conf"
    GLADE_DIR = "/usr/share/tcosconfig/"
    LOCALE_DIR = "/usr/share/locale"


# gettext support
setlocale( LC_ALL )
bindtextdomain( PACKAGE, LOCALE_DIR )
textdomain( PACKAGE )

# gentcos command (if svn exec in ./ path else use /usr/sbin/)
gentcos="sh gentcos"

# Default tcos suffix
tcos_suffix="-tcos1"

# selectable values and his keys (for tcos.conf file)
# using a bidimensional list
# var_VALUES= [ ['value1','text1'] , ['value2','text2']  ]
# value is saved in tcos.conf
# text can be translatable with _("translatable text")

TCOS_XORG_TYPE_VALUES=[ \
['R', _("Remote XDMCP") ] , \
['L', _("Local X") ], \
['S', _("SSH -X") ] , \
['N', _("Disable") ] \
]


TCOS_WEB_BROWSER_VALUES=[ \
['none', _("Disable") ] , \
['links2', _("Links2 browser") ], \
['dillo', _("Dillo browser") ] \
]


TCOS_REMOTEFS_VALUES=[ \
['none', _("Disable")], \
['ltspfs', _("LTSP filesystem") ], \
['shfs', _("SH filesystem") ] \
]


TCOS_METHOD_VALUES=[ \
['-nbi', _("Eherboot floppy") ], \
['-tftp', _("PXE booting") ], \
['-cdrom', _("CDROM booting") ] \
]


TCOS_USENFS_VALUES=[ \
['none', _("None") ], \
['nfs', _("Use NFS server") ], \
]
#pass
