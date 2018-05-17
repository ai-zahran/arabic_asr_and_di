#!/bin/bash
#: Title : produce_n_gram_lm.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Produce n-gram language model from Kaldi text file.
#: Arguments :
#  1- Path to kaldi text
#  2- Destination of the produced model

. ./path.sh


if [ $# -ne 2 ]; then
    echo "USAGE: produce_language_model.sh path/to/kaldi/text"
    exit 1
fi
text_path=$1
model_path=$2
corpus_path="../data/corpus"

# Transform Kaldi text file to the corpus format accepted by VariKN
python utils/Kaldi_text2VariKN_corpus.py $text_path $corpus_path

# Use VariKN to train a Kneser-Ney smoothed model from the corpus
# $VarKN_bin/counts2kn -an 4 -p 0.1 $corpus_path $model_path
$VarKN_bin/varigram_kn -a -D 0.001 -C -E 0.25 $corpus_path $model_path
rm -r $corpus_path
