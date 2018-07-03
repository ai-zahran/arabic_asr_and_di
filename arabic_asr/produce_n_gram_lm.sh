#!/bin/bash
#: Title : produce_n_gram_lm.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Produce n-gram language model from VariKN text file.
#: Arguments :
#  1- Path to VariKN corpus
#  2- Destination of the produced model

bash path.sh

if [ $# -ne 2 ]; then
    echo "USAGE: produce_language_model.sh path/to/varikn/corpus path/to/model"
    exit 1
fi
corpus_path=$1
model_path=$2

# Use VariKN to train a Kneser-Ney smoothed model from the corpus
$VariKN_bin/varigram_kn -a -D 0.001 -C -E 0.25 $corpus_path $model_path
