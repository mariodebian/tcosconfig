#!/bin/bash

_ARGS=$@
_PYTHON=/usr/bin/python2.4
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
