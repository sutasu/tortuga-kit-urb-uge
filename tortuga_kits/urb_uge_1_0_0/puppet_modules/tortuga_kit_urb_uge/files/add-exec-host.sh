 
#!/bin/sh

#############################################################################
#
# This code is the Property, a Trade Secret and the Confidential Information
# of Univa Corporation.
#
# Copyright 2008-2018 Univa Corporation. All Rights Reserved. Access is Restricted.
#
# It is provided to you under the terms of the
# Univa Term Software License Agreement.
#
# If you have any questions, please contact our Support Department.
#
# http://www.univa.com
#
#############################################################################

ARGS=$(getopt -o h -l "software-profile:,hardware-profile:,cell-dir:" -n "$0" -- "$@" );

if [ $? -ne 0 ]; then
    exit 1
fi

eval set -- "$ARGS";

slots=1

while true; do
    case "$1" in
        -h)
            shift;
            ;;
        --software-profile)
            shift;
            swprofilename="$1"
            shift;
            ;;
        --hardware-profile)
            shift;
            hwprofilename="$1"
            shift;
            ;;
        --cell-dir)
            shift;
            cell_dir="$1"
            shift;
            ;;
        --)
            shift;
            break;
            ;;
    esac
done

function usage() {
    echo "URB kit: usage: $0 [--software-profile NAME] [--hardware-profile NAME] --cell-dir CELL_DIR HOSTNAME"
    exit 1
}

# Validate argumens
if [ -z "$cell_dir" ] || [ -z "$1" ]; then
    usage
fi

hostName=$1

binDir=`dirname $0`
cd $binDir
binDir=`pwd`

if [ ! -d "$cell_dir" ]; then
    echo "URB kit: Error: cell directory $cell_dir does not exist"
    exit 1
fi

if [ ! -f $cell_dir/common/settings.sh ]; then
    echo "URB kit: UGE settings file not found in $cell_dir"
    exit 1
fi

. $cell_dir/common/settings.sh

echo "URB kit: On adding host: $hostName"

if ! grep -q 'urb=TRUE'; then
  EDITOR="$binDir/add-complex.sh" qconf -me $hostName
fi

exit 0
