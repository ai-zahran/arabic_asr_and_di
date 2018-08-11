#: Title : ctm2srt.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Produce SRT files from a CTM file
#: Arguments :
#  1- Path to CTM file
#  2- Destination of SRT files
#  3- Path to Kaldi words file

import argparse
import codecs
import os
from collections import defaultdict
from datetime import timedelta
from transliteration import transliterate

__author__ = "Ahmed Ismail"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "ahmed.ismail.zahran@gmail.com"
__status__ = "Development"


def parse_args():
    ''' Parses command line arguments

    Returns
    -------

    args : A dictionary of arguments
    '''
    # Arguments help strings
    ctm_file_path_help = 'Path to the CTM file.'
    srt_dir_path_help = 'Destination of the SRT directory.'
    words_file_path_help = 'Path to the Kaldi words file.'
    # Parse arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('ctm_file_path', type=str, help=ctm_file_path_help)
    arg_parser.add_argument('srt_dir_path', type= str, help=srt_dir_path_help)
    arg_parser.add_argument('words_file_path', type= str,
        help=words_file_path_help)
    args = vars(arg_parser.parse_args())
    return args


def make_word_map(words_file_path):
    word_map = dict()
    with codecs.open(words_file_path, 'r') as words_file:
        try:
            for line in words_file:
                word, word_num = line.strip().split()
                word_map[word_num] = word
        except Exception:
            print(('Word file is not in specified format. Each line '
                'should be in the form: <word> <word_number>'))
            exit(1)
    return word_map


def word_nums2words(line, word_map):
    line = ' '.join([word_map[word_num] for word_num in line.split()])
    return line


def format_time(time):
    time_sec_frac = int(round(time - int(time), 3) * 1000)
    time_sec = timedelta(seconds=int(time))
    return str(time_sec) + ',' + str(time_sec_frac).zfill(3)


def print_st(srt_file, index, lines, word_map, input_format=None,
    output_format=None):
    output = str(index + 1) + '\n'
    start_time = format_time(lines[0]['start_time'])
    end_time = format_time(lines[-1]['start_time'] +
                        lines[-1]['duration'])
    output += start_time + ' --> ' + end_time + '\n'
    st = ' '.join([line['word_num'] for line in lines])
    st = word_nums2words(st, word_map)
    if input_format != None and output_format != None:
        st = transliterate(st, input_format, output_format)
    elif input_format == None and output_format != None:
        raise Exception('Input format not specified.')
    elif input_format != None and output_format == None:
        raise Exception('Output format not specified.')
    output += st + '\n\n'
    srt_file.write(output)


def main():
    args = parse_args()
    ctm_file_path = args['ctm_file_path']
    srt_dir_path = args['srt_dir_path']
    words_file_path = args['words_file_path']
    input_format = 'buckwalter'
    output_format = 'unicode'

    word_map = make_word_map(words_file_path)

    duration = 5
    start_time = 0
    lines = []
    index = 0
    utterances = defaultdict(list)
    with codecs.open(ctm_file_path, 'r') as ctm_file:
        for line in ctm_file:
            line = line.strip().split()
            utterances[line[0]].append(line)
    
    for utt_id in utterances:
        srt_file_path = os.path.join(srt_dir_path, utt_id)
        srt_file = codecs.open(srt_file_path, 'w')
        for line in utterances[utt_id]:
            line = line.strip().split()
            line = {'utt_id': line[0], 'channel': line[1],
                    'start_time': float(line[2]),
                    'duration': float(line[3]), 'word_num': line[4],
                    'confidence': float(line[5])}
            if line['start_time'] >= start_time + duration:
                if lines != []:
                    print_st(srt_file, index, lines, word_map,
                            input_format, output_format)
                    index += 1
                lines = [line]
                start_time += duration
            else:
                lines.append(line)
        srt_file.close()

if __name__ == '__main__':
    main()