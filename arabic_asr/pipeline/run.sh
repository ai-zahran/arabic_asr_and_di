#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Run Arabic ASR pipeline

display_usage() {
    echo "Usage: run.sh [options]"
    echo "e.g.: run.sh -f data/1.wav"
    echo "main options (please specify exactly one option, unless otherwise" \
	"specified):"
    echo "  --conf              # configuration file containing the Kaldi"
    echo "                      # directory's path and the feature files"
    echo "                      # destination."
    echo "  -d|--dir            # directory containing wave files to perform"
    echo "                      # recognition on."
    echo "  -f|--file           # wave file to perform recognition on."
    echo "  -h|--help           # Display help"
    echo "  -r                  # find files recursively inside the directory"
    echo "                      # specified (only used when -d is used)."
    echo "Configuration file format:"
    echo "<var>=<value>"
    echo "e.g: kaldi_dir=/path/to/kaldi"
    echo "Each specification is set on a separate line."
    echo "Configuration options:"
    echo "  kaldi_dir           # Path to Kaldi directory (if not specified,"
    echo "                      # the script runs as if it is already inside"
    echo "                      # the Kaldi directory)."
    echo "  feat_dir            # Path to the directory to extract features to"
    echo "                      # Default is ./mfcc"

}

parse_conf() {
    # If no configuration file is specified, use default configuration file
    if [ $# -eq 0 ]; then
        conf_file_path=config
    else
        conf_file_path=$1
    fi
    
    if [ ! -f $conf_file_path ]; then
        echo "Error: Cannot find configuration file: $conf_file_path"
        exit 1
    fi

    # Parse configurations
    while IFS='=' read -r var val || [[ -n "$var" ]]; do
        case $var in
            kaldi_dir)
                kaldi_dir=$val
                ;;
            feat_dir)
                feat_dir=$val
                ;;
            *)
                echo "Error: Unknown configuration file option $var."
                exit 1
                ;;
        esac
        # if [ -n "$var $val" ]; then
        #     break
        # fi
    done < $conf_file_path

    # Process left-out configurations
    [ -n $kaldi_dir ] || [ $kaldi_dir != "" ] || [ kaldi_dir='.' ]
    [ -n $feat_dir ] || feat_dir='feats'

    [ -d $kaldi_dir ] || { echo "Cannot find Kaldi directory $kaldi_dir";
        exit 1; }

    echo "Using Kaldi dir at: $kaldi_dir"
    echo "Dumping features to: $feat_dir"
}

make_data_dir_from_file() {
    file_path=$1
    if [ ! -f $file_path ]; then
        echo "Error: Cannot find specified file: $file_path"
        exit 1
    fi
    data_dir='data/recs'
    [ -d $data_dir ] || mkdir $data_dir
    echo "rec $file_path" > $data_dir/wav.scp
    echo "rec rec" > $data_dir/utt2spk
    utils/utt2spk_to_spk2utt.pl $data_dir/utt2spk > $data_dir/spk2utt
}

make_data_dir_from_dir() {
    dir_path=$1
    if [ ! -d $dir_path ]; then
        echo "Error: Cannot find specified directory: $dir_path"
        exit 1
    fi
    file_paths=$(find $dir_path -name '*.wav')
    data_dir='data/recs'
    [ -d $data_dir ] || mkdir $data_dir
    echo "" > $data_dir/wav.scp
    echo "" > $data_dir/utt2spk
    for file_count in ${!file_paths[@]}; do
        file_path=${file_path[$file_count]}
        echo "rec_$file_count $file_path" >> $data_dir/wav.scp
        echo "rec_$file_count rec_$file_count" >> $data_dir/utt2spk
    done
    utils/utt2spk_to_spk2utt.pl $data_dir/utt2spk > $data_dir/spk2utt
}

# Script starts here

nj=1
recursive=0

if [ $# -eq 0 ]; then
    display_usage
    exit 1
fi

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            display_usage
            exit 0
            ;;
        -f|--file)
            shift
            if [ $# -gt 0 ]; then
                file_path=$1
            else
                echo "Error: No file specified."
                exit 1
            fi
            shift
            ;;
        -d|--dir)
            shift
            if [ $# -gt 0 ]; then
                dir_path=$1
            else
                echo "Error: No directory specified."
                exit 1
            fi
            shift
            ;;
        -r|--r)
            recursive=1
            shift
            ;;
        -o|--output)
	    shift
            output_dir=$1
            shift
            ;;
        *)
            echo "Unknown option $1"
            display_usage
            exit 1
            ;;
    esac
done

if [ -z $output_dir ]; then
    echo "Error: No output directory specified. Please specify an output" \
    "directory through -o."
    exit 1
fi
[ -d $output_dir ] || mkdir -p $output_dir || exit 1

# Define the model to use
eg_dir=egs/gale_arabic_2
model_dir=exp/nnet3/tdnn

# Read configuration
if [ -n $conf_path ]; then
    parse_conf $conf_path
else
    parse_conf
fi

# Produce a data directory from the specified files
cd $kaldi_dir/$eg_dir/s5
echo "Changed dir to $kaldi_dir/$eg_dir/s5"
. ./cmd.sh
. ./path.sh
if [ -n file_path ]; then
    make_data_dir_from_file $file_path
elif [ -n dir_path ]; then
    make_data_dir_from_dir $dir_path
else
    echo "Error: No files specified. Please specify a file through -f or a "
        "directory through -d."
fi

# Extract features and i-vectors
#steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" $data_dir \
#    exp/make_mfcc/rec $feat_dir || exit 1;
#steps/compute_cmvn_stats.sh $data_dir exp/make_mfcc/rec $feat_dir || exit 1;
#steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" \
#  --nj 1 $data_dir exp/ivector_extractor exp/ivectors_rec || exit 1;

# Decode
#steps/nnet3/decode.sh --nj 1 --cmd "$decode_cmd" --online-ivector-dir \
#    exp/ivectors_rec $model_dir/graph $data_dir $model_dir/decode

# Produce ctm from lattice
lattice-copy ark:"gunzip -c $model_dir/decode/lat.1.gz |" \
    ark,t:$model_dir/decode/lat.1
lattice-to-ctm-conf ark:$model_dir/decode/lat.1 output.ctm
python utils/ctm2srt.py output.ctm $output_dir data/lang/words.txt
