#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Run TDNN-BLSTM on MGB-challenge data.
#		 This script is based on the TDNN-BLSTM system specified in
#		 egs/swbd/s5c/local/chain/tuning/run_tdnn_blstm_1a.sh.

# End configuration section.
echo "$0 $@"    # Print the command line for logging

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

stage=0
train_stage=-10
get_egs_stage=-10

leftmost_questions_truncate=-1
xent_regularize=0.025
label_delay=0
chunk_width=150
chunk_left_context=40
chunk_right_context=40

ali_dir=exp/tri3a_ali
lang_dir=data/lang
train_dir_vp_sp=data/train_vp_sp
tree_dir=/media/ai/storage/kaldi/500hrs/exp/nnet3/chain/tree
ivector_dir=exp/ivectors_train
lat_dir=/media/ai/storage/kaldi/500hrs/exp/tri3a_lats
dir=/media/ai/storage/kaldi/500hrs/exp/nnet3/chain/tdnn_blstm

if ! cuda-compiled; then
    cat <<EOF && exit 1
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA
If you want to use GPUs (and have them), go to src/, and configure and make on a machine
where "nvcc" is installed.
EOF
fi

# At this stage, i-vectors have been extracted.

if [ $stage -le 1 ]; then
    # Get the alignments as lattices (gives the CTC training more freedom).
    # use the same num-jobs as the alignments
    nj=$(cat $ali_dir/num_jobs) || exit 1;
    steps/align_fmllr_lats.sh --nj $nj --cmd "$train_cmd" $train_dir_vp_sp \
        $lang_dir exp/tri3a $lat_dir
    rm $lat_dir/fsts.*.gz # save space
fi

if [ $stage -le 2 ]; then
    # Create a version of the lang/ directory that has one state per phone in the
    # topo file. [note, it really has two states.. the first one is only repeated
    # once, the second one has zero or more repeats.]
    rm -rf $lang_dir
    cp -r data/lang $lang_dir
    silphonelist=$(cat $lang_dir/phones/silence_phones.txt) || exit 1;
    nonsilphonelist=$(cat $lang_dir/phones/nonsilence_phones.txt) || exit 1;
    # Use our special topology... note that later on may have to tune this
    # topology.
    steps/nnet3/chain/gen_topo.py $nonsilphonelist $silphonelist >$lang_dir/topo
fi

if [ $stage -le 3 ]; then
    # Build a tree using our new topology.
    steps/nnet3/chain/build_tree.sh --frame-subsampling-factor 3 \
        --leftmost-questions-truncate $leftmost_questions_truncate \
        --context-opts "--context-width=2 --central-position=1" \
        --cmd "$train_cmd" 7000 $train_dir_vp_sp $lang_dir $ali_dir $treedir
fi

# Create configuration
if [ $stage -le 4 ]; then
    echo "$0: creating neural net configs using the xconfig parser";

    num_targets=$(tree-info $treedir/tree |grep num-pdfs|awk '{print $2}')
    [ -z $num_targets ] && { echo "$0: error getting num-targets"; exit 1; }
    learning_rate_factor=$(echo "print 0.5/$xent_regularize" | python)

    lstm_opts="decay-time=20"

    mkdir -p $dir/configs
    cat <<EOF > $dir/configs/network.xconfig
    input dim=100 name=ivector
    input dim=40 name=input

    # please note that it is important to have input layer with the name=input
    # as the layer immediately preceding the fixed-affine-layer to enable
    # the use of short notation for the descriptor
    fixed-affine-layer name=lda input=Append(-2,-1,0,1,2,ReplaceIndex(ivector, t, 0)) affine-transform-file=$dir/configs/lda.mat

    # the first splicing is moved before the lda layer, so no splicing here
    relu-renorm-layer name=tdnn1 dim=1024
    relu-renorm-layer name=tdnn2 input=Append(-1,0,1) dim=1024
    relu-renorm-layer name=tdnn3 input=Append(-1,0,1) dim=1024

    # check steps/libs/nnet3/xconfig/lstm.py for the other options and defaults
    fast-lstmp-layer name=blstm1-forward input=tdnn3 cell-dim=1024 recurrent-projection-dim=256 non-recurrent-projection-dim=256 delay=-3 $lstm_opts
    fast-lstmp-layer name=blstm1-backward input=tdnn3 cell-dim=1024 recurrent-projection-dim=256 non-recurrent-projection-dim=256 delay=3 $lstm_opts

    fast-lstmp-layer name=blstm2-forward input=Append(blstm1-forward, blstm1-backward) cell-dim=1024 recurrent-projection-dim=256 non-recurrent-projection-dim=256 delay=-3 $lstm_opts
    fast-lstmp-layer name=blstm2-backward input=Append(blstm1-forward, blstm1-backward) cell-dim=1024 recurrent-projection-dim=256 non-recurrent-projection-dim=256 delay=3 $lstm_opts

    fast-lstmp-layer name=blstm3-forward input=Append(blstm2-forward, blstm2-backward) cell-dim=1024 recurrent-projection-dim=256 non-recurrent-projection-dim=256 delay=-3 $lstm_opts
    fast-lstmp-layer name=blstm3-backward input=Append(blstm2-forward, blstm2-backward) cell-dim=1024 recurrent-projection-dim=256 non-recurrent-projection-dim=256 delay=3 $lstm_opts

    ## adding the layers for chain branch
    output-layer name=output input=Append(blstm3-forward, blstm3-backward) output-delay=$label_delay include-log-softmax=false dim=$num_targets max-change=1.5

    # adding the layers for xent branch
    # This block prints the configs for a separate output that will be
    # trained with a cross-entropy objective in the 'chain' models... this
    # has the effect of regularizing the hidden parts of the model.    we use
    # 0.5 / args.xent_regularize as the learning rate factor- the factor of
    # 0.5 / args.xent_regularize is suitable as it means the xent
    # final-layer learns at a rate independent of the regularization
    # constant; and the 0.5 was tuned so as to make the relative progress
    # similar in the xent and regular final layers.
    output-layer name=output-xent input=Append(blstm3-forward, blstm3-backward) output-delay=$label_delay dim=$num_targets learning-rate-factor=$learning_rate_factor max-change=1.5

EOF
    steps/nnet3/xconfig_to_configs.py --xconfig-file $dir/configs/network.xconfig --config-dir $dir/configs/
fi

if [ $stage -le 5 ]; then
    steps/nnet3/chain/train.py --stage $train_stage \
        --cmd "$decode_cmd" \
        --feat.online-ivector-dir $ivector_dir \
        --feat.cmvn-opts "--norm-means=false --norm-vars=false" \
        --chain.xent-regularize $xent_regularize \
        --chain.leaky-hmm-coefficient 0.1 \
        --chain.l2-regularize 0.00005 \
        --chain.apply-deriv-weights false \
        --chain.lm-opts="--num-extra-lm-states=2000" \
        --trainer.num-chunk-per-minibatch 64 \
        --trainer.frames-per-iter 1200000 \
        --trainer.max-param-change 2.0 \
        --trainer.num-epochs 4 \
        --trainer.optimization.shrink-value 0.99 \
        --trainer.optimization.num-jobs-initial 3 \
        --trainer.optimization.num-jobs-final 16 \
        --trainer.optimization.initial-effective-lrate 0.001 \
        --trainer.optimization.final-effective-lrate 0.0001 \
        --trainer.optimization.momentum 0.0 \
        --trainer.deriv-truncate-margin 8 \
        --egs.stage $get_egs_stage \
        --egs.opts "--frames-overlap-per-eg 0" \
        --egs.chunk-width $chunk_width \
        --egs.chunk-left-context $chunk_left_context \
        --egs.chunk-right-context $chunk_right_context \
        --egs.dir "$common_egs_dir" \
        --cleanup.remove-egs false \
        --feat-dir train_dir_vp_sp \
        --tree-dir $treedir \
        --lat-dir $lat_dir \
        --dir $dir || exit 1;
fi