#!/bin/bash

###
# A simple helper script to export the contents of a GDCE virtual machine disk image
###

VMDISK_INFO=$(qemu-img info /dev/vmdisk |grep virtual)
VM_SIZE=$(echo ${VMDISK_INFO} |awk '{print $3 " " $4}')
VM_SIZE_BYTES=$(echo ${VMDISK_INFO} |sed 's/[^[:digit:]]//g')
# If a remote filename is not provided just use the PVC name
REMOTE_FILENAME=${REMOTE_FILENAME:-${PVC_NAME}.raw}
DESTINATION=${RCLONE_REMOTE_PATH}/${REMOTE_FILENAME}

echo -e "\nReady to export PV ${PVC_NAME} (${VM_SIZE}) to ${DESTINATION}"
read -p "Proceed? (y/n) " confirmation

if [[ "$confirmation" == "y" ]]; then
  echo -e "\n🚛 Proceeding with VM disk export...\n"
  START_TIME=$(date +%s)

  nbdcopy --progress -- [ qemu-nbd --format raw /dev/vmdisk ] - | \
  rclone --s3-chunk-size 500Mi rcat ${DESTINATION}

  if [ $? -eq 0 ]; then
    END_TIME=$(date +%s)

    echo -e "\n\nExport completed successfully 🎊

Time taken: $(( ${END_TIME} - ${START_TIME} )) seconds
Local Disk Size:  $(echo ${VMDISK_INFO} |cut -d ' ' -f 3-)
Destination Size: $(rclone size ${DESTINATION} |tail -1  |cut -d ' ' -f 3-)
"
  fi

elif [[ "$confirmation" == "n" ]]; then
  echo -e "\n❌ Cancelled. No action taken.\n"
else
  echo "Invalid input. Please enter 'y' or 'n'."
fi

function print_errors() {

}
