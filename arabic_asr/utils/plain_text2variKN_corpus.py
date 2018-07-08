#: Title : plain_text2VariKN_corpus.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Transform plain text to VariKN corpus
#    through adding start and end tags
#: Arguments :
#  1- Path to plain text
#  2- Destination of VariKN corpus

import codecs
import argparse

__author__ = "Ahmed Ismail"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "ahmed.ismail.zahran@gmail.com"
__status__ = "Development"

def main():
    ''' Transforms plain text file to a VariKN corpus file
    '''
    # Parse command line arguments
    arg_parser = argparse.ArgumentParser(description=('Transform plain text'
        'file to coprus ready for processing by VariKN. '
        'Each sentence must be in a separate line.'))
    arg_parser.add_argument('plain_text', type=str,
        help=(('Path to the file containing the plain text corpus.')))
    arg_parser.add_argument('output_corpus', type=str,
        help=(('Path to output file to save the corpus.')))
    args = vars(arg_parser.parse_args())

    plain_text_file_path = args['plain_text']
    corpus_file_path = args['output_corpus']
    
    # Open the plain text file and the output corpus as streams
    # (It may be infeasible to perform offline processing in case of large
    # corpus files)
    plain_text_file = codecs.open(plain_text_file_path, 'r', encoding='utf-8')
    output_corpus_file = codecs.open(corpus_file_path, 'w', encoding='utf-8')
    
    # For each line in the plain text, remove the utterance-id and add
    # VariKN sentence start and end symbols (<s> and </s> respectively)
    for line in plain_text_file:
        line = '<s> ' + line.strip() + ' </s>\n'
        output_corpus_file.write(line)
    plain_text_file.close()
    output_corpus_file.close()


if __name__ == '__main__':
    main()
