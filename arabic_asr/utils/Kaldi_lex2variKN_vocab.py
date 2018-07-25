#: Title : Kaldi_lex2variKN_vocab.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Produce variKN vocabulary file from Kaldi lexicon
#: Arguments :
#  1- Path to Kaldi lexicon file
#  2- Destination of variKN vocabulary file

import argparse
import codecs

__author__ = "Ahmed Ismail"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "ahmed.ismail.zahran@gmail.com"
__status__ = "Development"

def main():
    ''' Extract vocabulary from lexicon
    '''
    # Parse command line arguments
    arg_parser = argparse.ArgumentParser(description=('Produce variKN '
        'vocabulary file from Kaldi lexicon.'))
    arg_parser.add_argument('lexicon', type=str,
        help=(('Path to the file containing the Kaldi lexicon.')))
    arg_parser.add_argument('vocab', type=str,
        help=(('Path to output file to save the variKN vocabulary.')))
    args = vars(arg_parser.parse_args())

    lexicon_file_path = args['lexicon']
    vocab_file_path = args['vocab']
    
    # Open the Kaldi lexicon file and the variKN vocabulary file as streams
    # (It may be infeasible to perform offline processing in case of large
    # files)
    lexicon_file = codecs.open(lexicon_file_path, 'r', encoding='utf-8')
    vocab_file = codecs.open(vocab_file_path, 'w', encoding='utf-8')
    
    # Write the sentence start and sentence end symbols
    vocab_file.write("<s>\n</s>\n")

    # For each line in the lexicon, remove the pronunciation and keep
    # the word only
    for line in lexicon_file:
        line = line.strip().split()[0] + '\n'
        vocab_file.write(line)
    lexicon_file.close()
    vocab_file.close()


if __name__ == '__main__':
    main()
