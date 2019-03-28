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

# helper script to add exec host

if [ "x$REPLACE_HOST" = "x" ]; then
    echo "REPLACE_HOST environment variable must be set"
    exit 1
fi

sed -i -e "s/^\(hostname[ ]*\)\(template\)$/\1$REPLACE_HOST/" -e "s/^\(complex_values[ ]*\).*/\1 tortuga=TRUE/" $1
