#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Build MIT-QCRI system for MGB-challenge Arabic DI task.

# Read training and development i-vectors directory paths
dialectID_repo_url="https://github.com/qcri/dialectID.git"

usage="Usage: run.sh <MGB3_dialectID_dir>"
eg="e.g.: run.sh data/ArabicDI"
dialectID_dir_help="Directory containing the MGB-3 Arabic DI repository."
if [ $# -ne 1 ]; then
    echo $usage
    echo $eg
    echo $dialect_ID_dir_help
fi
dialectID_dir_path=$1

if [ ! -d $dialectID_dir_path ]; then
    echo -n "Could not find dialect identification repository in the specified"
    echo " location"
    echo -n "Cloning the repository from $dialectID_repo_url"
    git clone $dialectID_repo_url $dialectID_dir_path || exit 1
fi

train_vardial_dir_path=$dialectID_dir_path/data/train.vardial2017/
dev_vardial_dir_path=$dialectID_dir_path/data/dev.vardial2017/

if [ ! -d $dev_vardial_dir_path ] || [ ! -d $train_vardial_dir_path ]; then
    echo -n "Could not find required data sets in the directory specified for"
    echo " the repository."
    echo -n "Remove the repository directory and run the script again to clone"
    echo " the repo."
    exit 1
fi

python dialect_identification.py $train_vardial_dir_path $dev_vardial_dir_path