#!/bin/bash

#
#   FIX-GLADE.sh
#   this is a script that patch glade image path to absolute paths
#
#


# EDIT THIS VARS
abs_path=/usr/share/tcosconfig/images/
_file=tcosconfig.glade

# all images separated by spaces
_images="tcos_config.png tcos-banner.png"

echo
echo "fix-glade.sh"
echo 
echo "patching ${_file}..."


make_backup() {
 cp ${_file} ${_file}.backup
}

restore_backup() {
 cp ${_file}.backup ${_file}
}

check_glade() {
 if [ $(cat ${_file}| wc -l) -gt 1 ]; then
   echo "glade seems ok"
 else
   echo "${_file} is empty restoring !!!"
   restore_backup
   exit 1
 fi
}

get_escaped() {
  value=$(echo "$1" | sed s/'\/'/'\\\/'/g)
  echo $value
}

patch_glade() {
  new_var=$(get_escaped ${abs_path})
  sed -i s/"${_image}"/"${new_var}${_image}"/g ${_file}
}

get_path() {
 value=$(grep $1 ${_file} | awk -F ">" '{split($2, A, "<") ; print A[1]}')
 echo $value
}


for _image in $_images; do
 if [ "$(get_path "${_image}")" = "${abs_path}${_image}" ]; then
   echo "${_file} already patched ${_image}"
 else
 echo "${_file} need patch"
   make_backup
   patch_glade "{_image}"
   check_glade
 fi
done

exit 0

