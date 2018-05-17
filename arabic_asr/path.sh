#!/bin/bash
#: Title : path.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Defines paths to programs used.

# This scripts defines paths to programs used.
# If a path does not exist, the script reports an error
VariKN_bin=''
if [ ! -d $VariKN_bin ]; then
 echo "VariKN binary directory not found in the path specified: $VariKN_bin"
