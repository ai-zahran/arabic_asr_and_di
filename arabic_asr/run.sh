#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Run the scripts to produce the model.

# Create n-gram language model

bash path.sh

data_dir=data
text_file_path=${data_dir}/text
if [ ! -f $text_file_path ]; then
    echo "Could not find corpus in the specified location: $text_file_path"
    exit 0
fi

python3 language_modeling/utils/plain_text2VariKN_text.py \
    $text_file_path ${text_file_path}_varikn

lang_modeling_dir=data/models/language_modeling
if [ ! -d $lang_modeling_dir ]; then
    mkdir -p $lang_modeling_dir
fi

n_gram_model_path=$lang_modeling_dir/model
sh $lang_modeling_dir/produce_n_gram_lm.sh $text_file_path $n_gram_model_path
