#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Build MIT-QCRI system for MGB-challenge Arabic DI task.

# Read training and development i-vectors directory paths
. ./path.sh || exit 1
cmd="run.pl"

. parse_options.sh || exit 1

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

if [ ! -d data ]; then
    mkdir data
fi

# Length Normalization
echo "Performing length normalization on i-vectors."

# Convert data to Kaldi-compatible ark format and perform length normalization
# using Kaldi's ivector-normalize-length
langs=(EGY GLF LAV MSA NOR)
for dir in $train_vardial_dir_path $dev_vardial_dir_path; do
    for lang in ${langs[@]}; do
        cat $dir/$lang.ivec | awk \
            '{printf "%s  [ ",$1;for (i=2;i<=NF;i++){printf "%f ",$i};printf "]\n"}' \
            > $dir/${lang}_kaldi.ivec
        ivector-normalize-length ark:$dir/${lang}_kaldi.ivec \
            ark,t:$dir/${lang}_normalized.ivec
    done
done

# Whitening transformation
echo "Computing whitening transforamtion."

# Compute whitening transformation from development set i-vectors
cat $dev_vardial_dir_path/*_normalized.ivec > \
    $dev_vardial_dir_path/dev_accumulated.ivec
est-pca --read-vectors=true --normaliza-mean=false --normalize-variance=true \
    --dim=-1 ark,t:$dev_vardial_dir_path/dev_accumulated.ivec transform.mat

# Apply whitening transformation to traning set i-vectors
for lang in ${langs[@]}; do
    transform-feats transform.mat \
        ark,t:$train_vardial_dir_path/${lang}_normalized.ivec \
        ark,t:$train_vardial_dir_path/${lang}_normalized_whitened.ivec \
        || exit 1
done

# Run Siamese neural network training
python dialect_identification.py $train_vardial_dir_path $dev_vardial_dir_path

