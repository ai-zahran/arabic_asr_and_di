#: Title : Kaldi_text2grapheme_lexicon.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Extract grapheme lexicon from Kaldi text
#: Arguments :
#  1- Path to kaldi text
#  2- Destination of the lexicon
#  3- Path to the nonsilence phones file [optional]

import argparse
import codecs
import os

__author__ = "Ahmed Ismail"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "ahmed.ismail.zahran@gmail.com"
__status__ = "Development"

def main():
    ''' Extract lexicon from Kaldi text
    '''
    # Parse command line arguments
    arg_parser = argparse.ArgumentParser(description=('Transforms Kaldi text'
        'file plain text.'))
    arg_parser.add_argument('kaldi_text', type=str,
        help=(('Path to the file containing the Kaldi text corpus.')))
    arg_parser.add_argument('output_lexicon', type=str,
        help=(('Path to output file to save the Kaldi lexicon.')))
    arg_parser.add_argument('--nonsilence-phones', dest='phones',
        type=str, help='Path to the nonsilence phones file [optional].')
    args = vars(arg_parser.parse_args())

    text_file_path = args['kaldi_text']
    lexicon_file_path = args['output_lexicon']
    if args['phones']:
        phones_file_path = args['phones']
    else:
        phones_file_path = None

    # If a list of phones is passed, read it
    if phones_file_path is not None:
        if os.path.exists(phones_file_path):
            with codecs.open(phones_file_path, 'r', encoding='utf-8') as \
                phones_file:
                phones = phones_file.readlines()
                phones = [phone.strip() for phone in phones]
        else:
            print(('Could not find nonsilence phones file in the specified '
                'location: %s.') % phones_file_path)
    else:
        phones = None

    # Open the Kaldi text file as a stream (It may be infeasible to perform
    # offline processing in case of a large Kaldi text file).
    with codecs.open(text_file_path, 'r', encoding='utf-8') as kaldi_text_file:

        # Initialize an empty set of words
        words = set()
        # For each line in the Kaldi text, remove the utterance-id and add the
        # words to the set of words
        for line in kaldi_text_file:
            line = ' '.join(line.split()[1:]) + '\n'
            words.update(line.strip().split())

    # Open the lexicon file as a stream
    with codecs.open(lexicon_file_path, 'w', encoding='utf-8') as \
        lexicon_file:
        # Sort and output the set of words to the grapheme dictionary, along
        # with their pronunciations
        # Grapheme dictionary line format: '<word> <list of graphemes>'
        words = sorted(words)
        for word in words:
            graphemes = list(word)
            # If the list of nonsilence phones is passed as an argument,
            # ignore words that include phones outside the user-specified
            # phone list
            grapheme_set = set(graphemes)
            if phones != None and not grapheme_set.issubset(phones):
                absent_graphemes = grapheme_set.difference(phones)
                print(('Warning: Ignoring word %s which contains graphemes '
                    'not found in the list passed.') % (word))
                print('Absent graphemes: %s.' % ', '.join(list(
                    absent_graphemes)))
                continue
            entry = '%s %s\n' % (word, ' '.join(graphemes))
            lexicon_file.write(entry)
        # Write the <UNK> entry
        lexicon_file.write("<UNK> spn")


if __name__ == '__main__':
    main()
