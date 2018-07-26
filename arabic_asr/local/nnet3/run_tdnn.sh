#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Run TDNN on MGB-challenge data.
#		 This script is based on the TDNN system specified in
#		 egs/teldium/s5_r2/local/nnet3/run_tdnn.sh, which is the
#		 standard TDNN system (at the time of writing).

ivector_dim=100
feat_dim=13

echo "$0 $@" # Print the command for logging

if [ -f cmd.sh ]; then . ./cmd.sh || exit 1; fi
if [ -f path.sh ]; then . ./path.sh; fi
. parse_options.sh || exit 1;

if [ $# != 6 ]; then
    echo "Usage: run_tdnn <feat-dir> <ivectors-dir> <lang-dir> <gmm-dir> <ali-dir> <target-dir>"
fi

feat_dir=$1
ivector_dir=$2
lang_dir=$3
gmm_dir=$4
ali_dir=$5
dir=$6

if ! cuda-compiled; then
  cat <<EOF && exit 1
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA
If you want to use GPUs (and have them), go to src/, and configure and make on a machine
where "nvcc" is installed.
EOF
else
  cat <<EOF
Cuda is installed.
EOF
fi

# Since high-resolution MFCC's were not used, we will not have to prepare
# low-resolution features (the authors of the Aalto system did not mention
# using high resolution MFCC's in their experiments).

# Create neural network configuration
echo "$0: creating neural net configs using the xconfig parser";
num_targets=$(tree-info $gmm_dir/tree |grep num-pdfs|awk '{print $2}')

mkdir -p $dir/configs
    cat <<EOF > $dir/configs/network.xconfig
    input dim=$ivector_dim name=ivector
    input dim=$feat_dim name=input  # For normal 13-dimensional MFCC's

    fixed-affine-layer name=lda input=Append(-2,-1,0,1,2,ReplaceIndex(ivector, t, 0)) affine-transform-file=$dir/configs/lda.mat

    relu-renorm-layer name=tdnn1 dim=850
    relu-renorm-layer name=tdnn2 dim=850 input=Append(-1,2)
    relu-renorm-layer name=tdnn3 dim=850 input=Append(-3,3)
    relu-renorm-layer name=tdnn4 dim=850 input=Append(-7,2)
    relu-renorm-layer name=tdnn5 dim=850 input=Append(-3,3)
    relu-renorm-layer name=tdnn6 dim=850
    output-layer name=output dim=$num_targets max-change=1.5
EOF

steps/nnet3/xconfig_to_configs.py --xconfig-file $dir/configs/network.xconfig --config-dir $dir/configs/

# Run TDNN training
steps/nnet3/train_dnn.py --stage=-10\
    --cmd="$decode_cmd" \
    --feat.online-ivector-dir=$ivector_dir \
    --feat.cmvn-opts="--norm-means=false --norm-vars=false" \
    --trainer.srand=0 \
    --trainer.max-param-change=2.0 \
    --trainer.num-epochs=3 \
    --trainer.samples-per-iter=400000 \
    --trainer.optimization.num-jobs-initial=2 \
    --trainer.optimization.num-jobs-final=12 \
    --trainer.optimization.initial-effective-lrate=0.0015 \
    --trainer.optimization.final-effective-lrate=0.00015 \
    --trainer.optimization.minibatch-size=256,128 \
    --cleanup.remove-egs=true \
    --use-gpu=true \
    --feat-dir=$feat_dir \
    --ali-dir=$ali_dir \
    --lang=$lang_dir \
    --dir=$dir


