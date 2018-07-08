#: Title : remove_spk_dir_speakers.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Remove speakers in one Kaldi directory from another Kaldi
# directory
#: Arguments :
#  1- Path to the Kaldi directory with the speakers to remove
#  2- Path to the Kaldi directory to remove the speakers from

import argparse
import codecs
import os


def remove_utterances(to_clean_utt_ids, to_clean_file_path, file_type):
    ''' Remove all entries from a file with speakers in the list passed.

    Arguments
    ---------

    to_clean_utt_ids : List of strings representing utterance id's to be
        removed with corresponding entries from the file.
    
    to_clean_file_path : Path of the file to be cleaned from entries with a
        speaker in the to_clean_utt_ids list.
    
    file_type : Type of the file.
        Possible values are:
        - wav.scp
        - segments
        - text
        - feats.scp
    '''

    to_clean_file_output = []
    file_types = ['wav.scp', 'segments', 'text', 'feats.scp']
    assert (file_type in file_types), ("Illegal file type %s."
        % file_type)

    if (not os.path.exists(to_clean_file_path)):
        print("Could not find %s file in specified location: %s." %
            (file_type, to_clean_file_path))
        exit(1)

    with codecs.open(to_clean_file_path, 'r') as to_clean_file:
        for line in to_clean_file:
            utt_id = line.strip().split()[0]
            if utt_id in to_clean_utt_ids:
                to_clean_file_output.append(line)

    print("Overwriting %s in first directory." % file_type)
    with codecs.open(to_clean_file_path, 'w') as to_clean_file:
        to_clean_file.write(''.join(to_clean_file_output))
    print("%d entries were written to the file." % len(to_clean_file_output))


def get_speaker_from_utt2spk(utt2spk_file_path):
    ''' Get a list of speakers in an utt2spk file

    Arguments
    ---------

    utt2spk_file_path : String representing the path to the utt2spk file
        to extract the list of speakers from.

    Returns
    -------

    spk_dir_speakers : List of strings representing speakers in the utt2spk
        file.
    '''
    spk_dir_speakers = set()
    print("Reading speakers in the second directory.")
    with codecs.open(utt2spk_file_path, 'r') as spk_dir_utt2spk_file:
        for line in spk_dir_utt2spk_file:
            spk_dir_speakers.add(line.strip().split()[1])
        print("Found %d speakers in the second directory."
            % len(spk_dir_speakers))
    return spk_dir_speakers


def clean_utt2spk(spk_dir_speakers, to_clean_utt2spk_file_path):
    ''' Remove entries with speakers in the list passed from the utt2spk file.
    
    Arguments
    ---------

    spk_dir_speakers : List of speakers to be removed.
    
    to_clean_utt2spk_file_path : String representing path to the file to
        remove speakers from.

    Returns
    -------

    to_clean_utt_ids : Utterance id's to keep in the directory being cleaned.

    '''
    to_clean_utt2spk = []
    to_clean_utt_ids = set()
    removed_speakers = set()
    print('Removing entries with speakers found.')
    with codecs.open(to_clean_utt2spk_file_path, 'r') as to_clean_utt2spk_file:
        for line in to_clean_utt2spk_file:
            utt_id, spk = line.strip().split()
            if spk not in spk_dir_speakers:
                to_clean_utt_ids.add(utt_id)
                to_clean_utt2spk.append(line)
            else:
                removed_speakers.add(spk)
    print(('Found %d speakers which exist simultaneously in both '
        'directories.') % len(removed_speakers))

    print("Overwriting utt2spk.")
    with codecs.open(to_clean_utt2spk_file_path, 'w') as to_clean_utt2spk_file:
        to_clean_utt2spk_file.write(''.join(to_clean_utt2spk))
    print("%d utterances kept." % len(to_clean_utt2spk))
    print("%d speakers removed from the first directory."
        % len(removed_speakers))

    return to_clean_utt_ids


def main():
    ''' Remove speakers in one Kaldi directory from another Kaldi directory.
    '''
        
    # Parse command line arguments
    arg_parser = argparse.ArgumentParser(description=('Remove speakers one '
        'Kaldi directory from another Kaldi directory.'))
    arg_parser.add_argument('to_clean_dir', type=str,
        help=(('Path to Kaldi directory to remove the speakers from.')))
    arg_parser.add_argument('spk_dir', type=str,
        help=(('Path to Kaldi directory containing speakers to be removed.')))
    args = vars(arg_parser.parse_args())

    to_clean_dir_path = args['to_clean_dir']
    spk_dir_path = args['spk_dir']

    to_clean_utt2spk_file_path = to_clean_dir_path + os.sep + 'utt2spk'
    to_clean_wav_file_path = to_clean_dir_path + os.sep + 'wav.scp'
    to_clean_seg_file_path = to_clean_dir_path + os.sep + 'segments'
    to_clean_text_file_path = to_clean_dir_path + os.sep + 'text'
    to_clean_feats_file_path = to_clean_dir_path + os.sep + 'feats.scp'
    spk_dir_utt2spk_file_path = spk_dir_path + os.sep + 'utt2spk'
    
    # Exit with error state 1 if utt2spk is not found in either directory.
    for file_path in [to_clean_utt2spk_file_path, spk_dir_utt2spk_file_path]:
        if (not os.path.exists(file_path)):
            print("Could not find utt2spk file in specified location: %s." %
                file_path)
            exit(1)
    
    # Get speakers in the utt2spk file from the first directory.
    spk_dir_speakers = get_speaker_from_utt2spk(spk_dir_utt2spk_file_path)

    # Keep entries in utt2spk file which do not contain speakers from
    # the previous directory and get corresponding utterance id's.
    to_clean_utt_ids = clean_utt2spk(spk_dir_speakers,
        to_clean_utt2spk_file_path)

    # If a segments file exists, remove entries in segments corresponding to
    # the list of utterance id's obtained.
    # If no segments file exists, do this for the wav.scp file.
    # Place the removed entries in the corresponding file for the opposite
    # directory.
    if os.path.exists(to_clean_seg_file_path):
        to_clean_file_path = to_clean_seg_file_path
        file_type = 'segments'
    else:
        to_clean_file_path = to_clean_wav_file_path
        file_type = 'wav.scp'
    remove_utterances(to_clean_utt_ids, to_clean_file_path, file_type)

    # Do the same for the Kaldi text and feats.scp files
    remove_utterances(to_clean_utt_ids, to_clean_text_file_path, 'text')
    remove_utterances(to_clean_utt_ids, to_clean_feats_file_path, 'feats.scp')

    return


if __name__ == '__main__':
    main()
