#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Build Aalto system for MGB-challenge.

. ./cmd.sh
. ./path.sh

nj=4
mfccdir="/media/ai/storage/data/500-hours_playground/feats/mfcc"
whole_dir=data/whole
train_dir=data/train
train_dir_cleaned=data/train_cleaned
train_dir_10000=data/train_10000
train_dir_vp=data/train_vp
train_dir_vp_sp=data/train_vp_sp
train_dir_vp_sp_20=data/train_dir_speed_pert_20
test_dir=data/test
lang_dir=data/lang


# ============= Feature extraction =============

# Extract MFCC's
steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" $whole_dir \
  exp/make_mfcc/whole $mfccdir

# Split the data into training and test sets based on speakers

# First, select the test set such that it forms about 20% of the whole data set
num_utts=$(< $whole_dir/segments wc -l)
num_utts_test=$(echo "$num_utts * 0.15" | bc)
num_utts_test=${utts_num_test%.*}
utils/subset_data_dir.sh --speakers $whole_dir $num_utts_test $test_dir

# Remove the test speakers from the training set and run Kaldi's
# fix_data_dir
if [ -d $train_dir ]; then
    rm -r $train_dir
fi
cp -r $whole_dir $train_dir
python utils/remove_test_speakers.py $train_dir $test_dir

# Remove extra utterances in any files with Kaldi's fix_data_dir
utils/spk2utt_to_utt2spk.pl $train_dir/utt2spk > $train_dir/spk2utt
utils/fix_data_dir.sh $train_dir

# Produce spk2utt file from utt2spk, then run Kaldi's fix_data_dir again
# to sort it
utils/fix_data_dir.sh $train_dir

# Select 10,000 shortest utterances in the training set and use them to
# train a monophone GMM
utils/subset_data_dir.sh --shortest $train_dir 10000 $train_dir_10000

# Compute CMVN stats
steps/compute_cmvn_stats.sh $train_dir exp/make_mfcc/train $mfccdir
steps/compute_cmvn_stats.sh $test_dir exp/make_mfcc/test $mfccdir
steps/compute_cmvn_stats.sh $train_dir_10000 \
  exp/make_mfcc/train_10000 $mfccdir


# ============= Language model =============

# Prepare language model directory
rm -r data/local/lang data/lang
rm data/local/dict/lexiconp.txt
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang $lang_dir

# Transform Kaldi corpus to the format used by variKN
python3 utils/Kaldi_text2variKN_corpus.py data/train/text \
  data/local/vocab.txt data/train/text_variKN

# Use variKN to produce Kneser-Ney smoothed n-gram model
python utils/Kaldi_lex2variKN_vocab.py data/local/dict/lexicon.txt \
  data/local/vocab.txt
steps/produce_n_gram_lm.sh data/train/text_variKN data/local/vocab.txt \
  data/local/lm_n_gram.arpa

# Use arpa to produce G.fst
arpa2fst --disambig-symbol=#0 --read-symbol-table=$lang_dir/words.txt \
  data/local/lm_n_gram.arpa $lang_dir/G.fst


# ============= Monophone model =============

# Train a monophone Gaussian Mixture Model (GMM)

steps/train_mono.sh --nj $nj --cmd "$train_cmd" $train_dir_10000 \
  $lang_dir exp/mono

# Build decoding graph for the monophone GMM
utils/mkgraph.sh $lang_dir exp/mono exp/mono/graph

# Decode using the monophone GMM
steps/decode.sh --nj $nj --cmd "$decode_cmd" exp/mono/graph $test_dir \
  exp/mono/decode

# Extract alignments for the monophone GMM
steps/align_si.sh --nj $nj --cmd "$train_cmd" $train_dir_10000 $lang_dir \
  exp/mono exp/mono_ali


# ============= Tri-phone models =============

# Train a tri-phone GMM using alignments generated by the previous model
# for initialization
steps/train_deltas.sh --cmd "$train_cmd" 2000 15000 $train_dir $lang_dir \
  exp/mono_ali exp/tri1

# Build decoding graph
utils/mkgraph.sh $lang_dir exp/tri1 exp/tri1/graph

# Decode using the tri-phone model
steps/decode.sh --nj $nj --cmd "$decode_cmd" exp/tri1/graph $test_dir \
  exp/tri1/decode

# Extract alignments for the tri-phone GMM
steps/align_si.sh --nj $nj --cmd "$train_cmd" $train_dir $lang_dir \
  exp/tri1 exp/tri1_ali

# Train a tri-phone GMM on top of features transformed with Linear
# Discriminant Analysis (LDA) using alignments generated by the
# previous model for initialization
steps/train_lda_mllt.sh --cmd "$train_cmd" --splice-opts \
  "--left-context=3 --right-context=3" 2500 15000 $train_dir $lang_dir \
  exp/tri1_ali tri2a/exp

# Build decoding graph
utils/mkgraph.sh $lang_dir exp/tri2a exp/tri2a/graph

# Decode using the LDA-MLLT tri-phone model
steps/decode.sh --nj $nj --cmd "$decode_cmd" exp/tri2a/graph $test_dir \
  exp/tri2a/decode

# Extract alignments for the LDA-MLLT tri-phone GMM
steps/align_si.sh --nj $nj --cmd "$train_cmd" $train_dir $lang_dir \
  exp/tri2a exp/tri2a_ali

# Train a Spearker Adaptive Training (SAT) tri-phone GMM using alignments
# generated by the previous model for initialization
steps/train_sat.sh --cmd "$train_cmd" 4200 40000 $train_dir $lang_dir \
  exp/tri2a_ali exp/tri2b

# Extract alignments for the SAT tri-phone GMM
steps/align_si.sh --nj $nj --cmd "$train_cmd" $train_dir $lang_dir \
  exp/tri2b exp/tri2b_ali


# ============= Cleaning and segmenting =============
# Run clean and segment scripts
steps/cleanup/clean_and_segment_data.sh $train_dir $lang_dir exp/tri2b \
  exp/tri2b_cleanup $train_dir_cleaned


# ============= i-vector and TDNN training =============

steps/compute_cmvn_stats.sh $train_dir_cleaned \
  exp/make_mfcc/train_cleaned $mfccdir

# Extract alignments for the the SAT tri-phone GMM
steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" $train_dir_cleaned \
  $lang_dir exp/tri2b exp/tri2b_cleanup_ali

# Train a Spearker Adaptive Training (SAT) tri-phone GMM on the cleaned
# and segmented data using alignments generated by the cleaned model for
# initialization
steps/train_sat.sh --cmd "$train_cmd" 4200 40000 $train_dir_cleaned \
  $lang_dir exp/tri2b_cleanup_ali exp/tri3a

# Perform volume and speed perturbation
cp -r $train_dir $train_dir_vp
utils/data/perturb_data_dir_volume.sh $train_dir_vp
utils/data/perturb_data_dir_speed_3way.sh $train_dir_vp \
  $train_dir_vp_sp

# Compute MFCC's and perform CMVN for perturbed data
steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" $train_dir_vp_sp \
  exp/make_mfcc/train_vp_sp $mfccdir
steps/compute_cmvn_stats.sh $train_dir_vp_sp exp/make_mfcc/train_vp_sp \
  $mfccdir

# Extract alignments for the SAT tri-phone GMM
steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" $train_dir_vp_sp \
  $lang_dir exp/tri3a exp/tri3a_ali

# Train an LDA+MLLT system using alignments from the previous SAT model to
# extract LDA+MLLT transforms, which will be used in LDA-based i-vector
# training
steps/train_lda_mllt.sh --cmd "$train_cmd" 2500 15000 $train_dir_vp_sp \
  $lang_dir exp/tri3a_ali exp/tri3b

# Extract a 20% subset of the training data for universal background model
# UBM-GMM training
num_utts_train_vp_sp=$(< $train_dir_vp_sp/segments wc -l)
num_utts_20=$(perl -e "print int($num_utts_train * 0.2); ")
utils/subset_data_dir.sh $train_dir_vp_sp $num_utts_20 \
  $train_dir_vp_sp_20

# Build UBM-GMM using the LDA GMM trained earlier
steps/online/nnet2/train_diag_ubm.sh $train_dir_vp_sp_20 1024 \
  exp/tri3b exp/diag_ubm

# Train i-vector extractor
steps/online/nnet2/train_ivector_extractor.sh --cmd "$train_cmd" --nj 1 \
  --ivector-dim 1000 $train_dir_vp_sp exp/diag_ubm exp/ivector_extractor

# Extract i-vectors

