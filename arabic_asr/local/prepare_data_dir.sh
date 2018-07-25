#!/bin/bash
#: Title : prepare_data_dir.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Prepare Kaldi data directory from TDF files in an LDC corpus
#: Input : - Path of TDF corpus files directory
#          - Destination of Kaldi the data directory

# Read arguments
usage="USAGE: prepare_data_dir.sh <LDC_corpus> <Kaldi_data_dir>"
eg="e.g.: prepare_data_dir.sh local/gale_p2_arb_bc_transcripts_p1 data"
ldc_corpus_help="  LDC_corpus: String specifying the path to the LDC"
ldc_corpus_help="$ldc_corpus_help transcript corpus."
kaldi_data_dir_help="  Kaldi_data_dir: String specifying the destination to"
kaldi_data_dir_help="$kaldi_data_dir_help the Kaldi data directory."

if [ $# -ne 2 ]; then
    echo $usage
    echo $eg
    echo "arguments:"
    echo $ldc_corpus_help
    echo $kaldi_data_dir_help
fi

ldc_corpus=$1
kaldi_data_dir=$2

# Check arguments

if [ ! -d $ldc_corpus ]; then
    error_msg="Error: LDC corpus directory does not exist in the specified "
    error_msg="location: $ldc_corpus."
    echo error_msg
    exit 1
fi

# Make Kaldi data directory
if [ -d $kaldi_data_dir ]; then
    error_msg="Error: A Kaldi data directory already exists at the specified"
    error_msg="$error_msg location and its files cannot be deleted. Please"
    error_msg=" make sure the directory is empty."
    rm -r $kaldi_data_dir || [ $(echo $error_msg && exit 1) ]
fi

error_msg="Error: Could not create Kaldi data directory at the specified "
error_msg="$error_msg: location $kaldi_data_dir."
mkdir $kaldi_data_dir || [ $(echo $error_msg && exit 1)

# Produce Kaldi data dir for each file in the LDC corpus
# Append similar files together
num_processed=0
for ldc_file in $ldc_corpus/*.tdf; do
    success_msg="Successfully created Kaldi files for ldc corpus file "
    success_msg="$success_msg $ldc_file"
    error_msg="Error: Could not create Kaldi files for ldc corpus file "
    error_msg="$error_msg $ldc_file"
    success=0
    python utils/ldc_corpus2kaldi_dir.py $ldc_file $kaldi_data_dir \
        --ignore-absent && success=1
    if [ $success == 1 ]; then
        echo $success_msg
        num_processed=$((num_processed + 1))
    else
        echo $error_msg
    fi
done

if [ $num_processed == 0 ]; then
    warning_msg="Warning: No LDC corupus files found in the specified "
    warning_msg=" directory: $ldc_corpus. Make sure files exist in tdf format."
else
    echo "Successfully processed $num_processed LDC files."
fi
