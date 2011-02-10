#!/bin/bash
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
_ARGS=$@
_PYTHON=/usr/bin/python
_CMD="${_PYTHON} /usr/share/tcosconfig/tcosconfig.py ${_ARGS}"
_DESKTOP=/usr/share/applications/tcosconfig.desktop



# launcher script of tcosconfig python tool

if [ $UID = 0 ]; then
  #echo "Run as root, good !!!"
  ${_CMD}
else
  #echo "Exec by user, need root access"
  # search a X su tool
  if [ -x /usr/bin/gksu ]; then
    _SUCMD="/usr/bin/gksu -a --desktop ${_DESKTOP} "
  elif [ -x /usr/bin/kdesu ]; then
    _SUCMD="/usr/bin/kdesu -c"
  elif [ -x /usr/bin/xsu ]; then
    _SUCMD="/usr/bin/xsu"
  else
    _SUCMD=""
    echo "Error while trying to search a X su tool (gksu, kdesu, xsu)"
    echo "Run tcosconfig as root !!!"
    exit 1
  fi
 ${_SUCMD} "${_CMD}"
fi

exit 0
