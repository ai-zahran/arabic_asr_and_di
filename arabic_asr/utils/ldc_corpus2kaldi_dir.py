#: Title : ldc_corpus2kaldi_dir.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Transform the LDC corpus to a Kaldi data directory
#: Arguments :
#  1- Path to the TDF file
#  2- Destination of the Kaldi data directory

import argparse
import codecs
import csv
import numpy as np
import os
import pandas as pd

def parse_args(arg_info):
    ''' Parses command line arguments

    Arguments
    ---------

    arg_info : List of dictionaries containing information about arguments

    Returns
    -------

    args : A dictionary of arguments
    '''
    args = []
    # Parse arguments
    arg_parser = argparse.ArgumentParser()
    for arg in arg_info:
        arg_parser.add_argument(arg['name'], type=arg['type'], help=arg['help'])
    args = vars(arg_parser.parse_args())
    return args


def transliterate(text, mapping):
    ''' Transliterates text using the specified mapping

    Arguments
    ---------

    text : String containing the text to transliterate.

    mapping : Dictionary with letters as key and their transliterations as.
    values.

    Returns
    -------

    text : String containing transliterated text.
    '''
    text = ''.join([mapping[c] if c in mapping else c for c in text])
    return text


def main():

    # Arguments help strings
    tdf_file_path_help = 'Path to the tdf file.'
    kaldi_data_dir_path_help = 'Destination of the Kaldi directory.'
    # Unicode dictionary
    unicode2buckwalter_dict = {u'\u0621': '\'', u'\u0622': '|', u'\u0623': '>',
        u'\u0624': '&', u'\u0625': '<', u'\u0626': '}', u'\u0627': 'A',
        u'\u0628': 'b', u'\u0629': 'p', u'\u062A': 't', u'\u062B': 'v',
        u'\u062C': 'j', u'\u062D': 'H', u'\u062E': 'x', u'\u062F': 'd',
        u'\u0630': '*', u'\u0631': 'r', u'\u0632': 'z', u'\u0633': 's',
        u'\u0634': '$', u'\u0635': 'S', u'\u0636': 'D', u'\u0637': 'T',
        u'\u0638': 'Z', u'\u0639': 'E', u'\u063A': 'g', u'\u0640': '_',
        u'\u0641': 'f', u'\u0642': 'q', u'\u0643': 'k', u'\u0644': 'l',
        u'\u0645': 'm', u'\u0646': 'n', u'\u0647': 'h', u'\u0648': 'w',
        u'\u0649': 'Y', u'\u064A': 'y', u'\u064B': 'F', u'\u064C': 'N',
        u'\u064D': 'K', u'\u064E': 'a', u'\u064F': 'u', u'\u0650': 'i',
        u'\u0651': '~', u'\u0652': 'o', u'\u0670': '`', u'\u0671': '{'}

    # Parse arguments
    arg_info = [{'name': 'tdf_file_path', 'type': str, 'help':
        tdf_file_path_help},
        {'name': 'kaldi_data_dir_path', 'type': str, 'help':
        kaldi_data_dir_path_help}]
    args = parse_args(arg_info)
    tdf_file_path = args['tdf_file_path']
    kaldi_data_dir_path = args['kaldi_data_dir_path']
    foreign_lang_pattern = '<foreign language=".*"> </foreign>'
    wav_scp_file_path = kaldi_data_dir_path + os.sep + 'wav.scp'
    segments_file_path = kaldi_data_dir_path + os.sep + 'segments'
    text_file_path = kaldi_data_dir_path + os.sep + 'text'
    utt2spk_file_path = kaldi_data_dir_path + os.sep + 'utt2spk'

    # Read tdf (tab-delimited format) file from the user-specified path
    if not os.path.exists(tdf_file_path):
        print('Error: Cannot find the tdf file in the path specified: %s.' %
            tdf_file_path)
        return 1
    tdf_df = pd.read_csv(tdf_file_path, sep='\t')

    # Remove comments (lines starting with ';;') from the tdf file
    tdf_df = tdf_df[~tdf_df['file;unicode'].str.startswith(';;')]
    # Drop irrelevant columns
    cols_to_drop = ['section;int', 'turn;int', 'segment;int',
        'sectionType;unicode', 'suType;unicode']
    tdf_df = tdf_df.drop(columns=cols_to_drop)
    print('Dropping columns: %s.' % ', '.join(cols_to_drop))
    print('Successfully dropped columns: %s.' % ', '.join(cols_to_drop))
    print('Columns in the Dataframe are:')
    print(tdf_df.columns)

    # Remove foreign language utterances
    print('Removing utterances in foreign lanuages.')
    tdf_df = tdf_df[~tdf_df['transcript;unicode'].str.contains(
        foreign_lang_pattern)]
    print('Successfully removed utterances in foreign lanuages.')

    # Remove non-MSA tags (since we will be working with a grapheme model)
    print(('Removing <non-MSA> tags (since we will be working with a '
        'grapheme model).'))
    tdf_df['transcript;unicode'] = tdf_df['transcript;unicode'].apply(
        lambda x: x.replace('<non-MSA>', ''))
    print('Successfully removed <non-MSA> tags.')

    # Transliterate the text according to Buckwalter transliteration
    print('Transliterating text according to Buckwalter transliteration.')
    tdf_df['transcript;unicode'] = tdf_df['transcript;unicode'].apply(
        lambda x: transliterate(x, unicode2buckwalter_dict))

    # Save the data to a Kaldi data directory

    # Create the Kaldi data directory
    print('Creating Kaldi data directory at %s.' % kaldi_data_dir_path)
    if os.path.isdir(kaldi_data_dir_path):
        print(('Warning: Kaldi directory already exists in the path '
            'specified: %s. Files will be appended.') %
            kaldi_data_dir_path)
    else:
        try:
            os.makedirs(kaldi_data_dir_path)
        except OSError:
            print(('Error: Could not create directory at specified location: '
                '%s.') % kaldi_data_dir_path)
            return 1
    print('Successfully created Kaldi data directory.')

    # Output the data to the files in the format accepted by Kaldi
    # The value of column 'file;unicode' is used as utterance id (utt-id)
    # Segment id is <file;unicode>-<start;float>-<end;float>

    # wav.scp: <utt-id> /path/to/wave/file
    # path to wave file is the same as the utt-id, with .wav extension instead
    # of .sph
    print('Saving wav.scp file to %s.' % wav_scp_file_path)
    tdf_df['file-path'] = tdf_df['file;unicode'].apply(lambda x:
        os.path.splitext(x)[0] + '.wav')
    to_print = ['file;unicode', 'file-path']
    tdf_df[to_print].drop_duplicates().to_csv(wav_scp_file_path, mode='a',
        sep=' ', header=False, index=False)
    print('Successfully saved wav.scp.')

    # segments: <segment-id> <utt-id> start-time end-time
    print('Saving segments file to %s.' % segments_file_path)
    tdf_df['segment-id'] = tdf_df.apply(lambda row: '%s_%s-%s' %
        (row['file;unicode'], str(row['start;float']),
        str(row['end;float'])), axis=1)
    to_print = ['segment-id', 'file;unicode', 'start;float', 'end;float']
    tdf_df[to_print].to_csv(segments_file_path, mode='a', sep=' ',
        header=False, index=False)
    print('Successfully saved segments file.')

    # text: <utt-id> <utterance>
    print('Saving text file to %s.' % text_file_path)
    to_print = ['segment-id', 'transcript;unicode',]
    tdf_df[to_print].to_csv(text_file_path, mode='a', sep='\t', header=False,
        index=False)
    print('Successfully saved text segments file.')

    # utt2spk: <utt-id> <speaker>
    # Use Utterance-id as a prefix to the speaker name to avoid ambiguity
    # (some speakers are named as 'speaker 1' for example, so 'speaker 1'
    # will exist in multiple LDC tdf files, although the speakers are
    # different)
    print('Saving utt2spk to %s.' % utt2spk_file_path)
    tdf_df['speaker;unicode'] = tdf_df.apply(lambda row: '%s-%s' % (
        str(row['file;unicode']), str(row['speaker;unicode'])),
        axis=1)
    to_print = ['segment-id', 'speaker;unicode',]
    tdf_df[to_print].to_csv(utt2spk_file_path, mode='a', sep=' ',
        header=False, index=False)
    print('Successfully saved utt2spk.')

    return 0


if __name__ == '__main__':
    main()