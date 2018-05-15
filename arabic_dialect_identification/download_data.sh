#!/bin/bash
#: Title : download_data.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Download the MGB-3 challenge Arabic dialect identification
#     dataset.
#: Arguments :
#  1- Path to urls file
#   Download link:
#   https://github.com/qcri/dialectID/blob/master/data/train.vardial2017/wav.lst
#  2- Destination to download wav files

if [$# -ne 2]; then
    echo "Incorrect number of arguments ($# arguments passed)."
    echo "Usage: sh download_data.sh </path/to/url/file.txt> </path/to/destination/dir>"
    exit 1
fi

url_file=$1
dst_dir=$2

while read url
do
    wget $url -P $dst_dir/$link
done < $url_file
