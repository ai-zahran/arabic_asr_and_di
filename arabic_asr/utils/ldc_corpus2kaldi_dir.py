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
from transliteration import transliterate


def parse_args():
    ''' Parses command line arguments

    Returns
    -------

    args : A dictionary of arguments
    '''
    # Arguments help strings
    tdf_file_path_help = 'Path to the tdf file.'
    kaldi_data_dir_path_help = 'Destination of the Kaldi directory.'
    ignore_absent_help = ('If set, characters absent from the target '
        'character set will be ignored in the transliteration. If not, '
        'absent characters will be output without mapping in the '
        'transliteration.')
    # Parse arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('tdf_file_path',
        type=str, help=tdf_file_path_help)
    arg_parser.add_argument('kaldi_data_dir_path', type= str,
        help=kaldi_data_dir_path_help)
    arg_parser.add_argument('--ignore-absent', action='store_true',
        help=ignore_absent_help)
    args = vars(arg_parser.parse_args())
    return args


def main():

    # Parse arguments
    args = parse_args()
    tdf_file_path = args['tdf_file_path']
    kaldi_data_dir_path = args['kaldi_data_dir_path']
    ignore_absent = args['ignore_absent']

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

    # Remove utterances where end time is not larger than start time
    tdf_df = tdf_df[tdf_df['start;float'] < tdf_df['end;float']]

    # Transliterate the text according to Buckwalter transliteration
    print('Transliterating text according to Buckwalter transliteration.')
    tdf_df['transcript;unicode'] = tdf_df['transcript;unicode'].apply(
        lambda x: transliterate(x, 'unicode', 'buckwalter', ignore_absent))

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

    # Strip and remove spaces from speaker and file name to avoid errors from
    # Kaldi
    # Create a new file name column for this purpose (the original will be used
    # in computing the path to the wave file)
    tdf_df['file-name'] = tdf_df['file;unicode'].str.replace(
        ' ', '')
    tdf_df['speaker;unicode'] = tdf_df['speaker;unicode'].str.replace(
        ' ', '')

    # wav.scp: <utt-id> /path/to/wave/file
    # path to wave file is the same as the utt-id, with .wav extension instead
    # of .sph
    print('Saving wav.scp file to %s.' % wav_scp_file_path)
    tdf_df['file-path'] = tdf_df['file;unicode'].apply(lambda x:
        os.path.splitext(x)[0] + '.wav')
    to_print = ['file-name', 'file-path']
    tdf_df[to_print].drop_duplicates().to_csv(wav_scp_file_path, mode='a',
        sep=' ', header=False, index=False)
    print('Successfully saved wav.scp.')

    # segments: <segment-id> <utt-id> start-time end-time
    # Segment id = <speaker>-<file-name>_<start-time>-<end-time>
    # (making speaker-id's prefixes of utterance-id's is related to Kaldi)
    print('Saving segments file to %s.' % segments_file_path)
    tdf_df['segment-id'] = tdf_df.apply(lambda row: '%s-%s_%s-%s' %
        (row['speaker;unicode'], row['file-name'], str(row['start;float']),
        str(row['end;float'])), axis=1)
    # Strip and remove spaces from segment-id to avoid errors from Kaldi
    tdf_df['segment-id'] = tdf_df['segment-id'].str.strip().replace(' ', '')
    to_print = ['segment-id', 'file-name', 'start;float', 'end;float']
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
    # Use utt-id as a postfix to the speaker name to avoid ambiguity
    # (some speakers are named as 'speaker 1' for example, so 'speaker 1'
    # will exist in multiple LDC tdf files, although the speakers are
    # different)
    print('Saving utt2spk to %s.' % utt2spk_file_path)
    tdf_df['speaker;unicode'] = tdf_df.apply(lambda row: '%s-%s' % (
        str(row['speaker;unicode']), str(row['file-name'])),
        axis=1)

    to_print = ['segment-id', 'speaker;unicode',]
    tdf_df[to_print].to_csv(utt2spk_file_path, mode='a', sep=' ',
        header=False, index=False)
    print('Successfully saved utt2spk.')

    return 0


if __name__ == '__main__':
    main()