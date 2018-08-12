#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Run adaptation on MGB-3 challenge data.

ivector_dim=100
feat_dim=13

echo "$0 $@" # Print the command for logging

if [ -f cmd.sh ]; then . ./cmd.sh || exit 1; fi
if [ -f path.sh ]; then . ./path.sh; fi
. parse_options.sh || exit 1;

if [ $# != 6 ]; then
    echo "Usage: run_adaptation <feat-dir> <ivectors-dir> <dev-dir> "
        "<lang-dir> <ali-dir> <model-dir> <target-dir>"
fi

feat_dir=$1
ivector_dir=$2
dev_dir=$3
lang_dir=$4
ali_dir=$5
model_dir=$6
dir=$7

cp -r $model_dir $dir

# Run TDNN training using the last model and 
last_model=$(ls $dir/[0-9]*.mdl | tail -1) # The last numbered model
last_model_num=${last_model%.mdl}
steps/nnet3/train_dnn.py --stage=$last_model_num\
    --cmd="$decode_cmd" \
    --feat.online-ivector-dir=$ivector_dir \
    --feat.cmvn-opts="--norm-means=false --norm-vars=false" \
    --trainer.srand=0 \
    --trainer.max-param-change=2.0 \
    --trainer.num-epochs=3 \
    --trainer.samples-per-iter=400000 \
    --trainer.optimization.num-jobs-initial=1 \
    --trainer.optimization.num-jobs-final=1 \
    --trainer.optimization.minibatch-size=256,128 \
    --cleanup.remove-egs=true \
    --use-gpu=true \
    --feat-dir=$feat_dir \
    --ali-dir=$ali_dir \
    --lang=$lang_dir \
    --dev-dir=$dev_dir
    --dir=$dir
