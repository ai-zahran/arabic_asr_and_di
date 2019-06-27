#!/bin/bash
#: Title : path.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Defines paths to programs used.

# This scripts defines paths to programs used.
# If a path does not exist, the script reports an error

# Read program paths from paths.txt
paths_file="paths.txt"
echo "Reading paths to program directories"
while IFS=': ', read -r program_name program_path; do
    if [ "$line" != "" ]; then
        continue
    elif  [ ${program_name,,} = 'varikn' ]; then
        export VariKN_bin=$program_path
        echo "VariKN path set to $program_path"
    fi
done < $paths_file


if [ ! -d $VariKN_bin ]; then
    echo "VariKN binary directory not found in the path specified: $VariKN_bin"
fi

export KALDI_ROOT=`pwd`/../../..
[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export LC_ALL=C
