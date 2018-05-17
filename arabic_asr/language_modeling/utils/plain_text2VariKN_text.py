#: Title : plain_text2VariKN_corpus.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Transform plain text to VariKN corpus
#    through adding start and end tags
#: Arguments :
#  1- Path to plain text
#  2- Destination of VariKN corpus

import io
import argparse


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

    path_to_text = args['plain_text']
    path_to_corpus = args['output_corpus']
    
    # Open the plain text file and the output corpus as streams
    # (It maybe infeasible to perform offline processing in case of large
    # corpus files)
    plain_text = io.open(path_to_text, 'r')
    output_corpus = io.open(path_to_corpus, 'w')
    
    # For each line in the plain text, remove the utterance-id and add
    # VariKN sentence start and end symbols (<s> and </s> respectively)
    for line in plain_text:
        line = '<s> ' + line.strip() + ' </s>\n'
        output_corpus.write(line)
    plain_text.close()
    output_corpus.close()


if __name__ == '__main__':
    main()
