#: Title : Kaldi_text2plain.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Transform Kaldi text to plain text
#    through removing utterance id
#: Arguments :
#  1- Path to kaldi text
#  2- Destination of plain text

import io
import argparse


def main():
    ''' Transforms Kaldi text text to plain text through removing utterance id
    '''
    # Parse command line arguments
    arg_parser = argparse.ArgumentParser(description=('Transform Kaldi text'
        'file to coprus ready for processing by VariKN.'))
    arg_parser.add_argument('kaldi_text', type=str,
        help=(('Path to the file'
            'containing the Kaldi text corpus.')))
    arg_parser.add_argument('output_corpus', type=str,
        help=(('Path to output'
            'file to save the corpus as plain text.')))
    args = vars(arg_parser.parse_args())

    path_to_text = args['kaldi_text']
    path_to_corpus = args['output_corpus']
    
    # Open the Kaldi text file and the output corpus as streams
    # (It maybe infeasible to perform offline processing in case of large
    # Kaldi text files)
    kaldi_text = io.open(path_to_text, 'r')
    output_corpus = io.open(path_to_corpus, 'w')
    
    # For each line in the Kaldi text, remove the utterance-id
    for line in kaldi_text:
        line = ' '.join(line.split()[1:]) + '\n'
        output_corpus.write(line)
    kaldi_text.close()
    output_corpus.close()


if __name__ == '__main__':
    main()
