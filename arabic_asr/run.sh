#!/bin/bash
#: Title : run.sh
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Run the scripts to produce the model.

# Create n-gram language model
text_file_path=''
model_file_path=''
lang_modeling_dir=''
sh $lang_modeling_dir/produce_n_gram_lm.sh $text $model_file_path
