import codecs
import numpy as np
import os
import pandas as pd


def read_ivectors_from_file(ivecs_file_path):
    '''Reads i-vectors from a file
    
    Arguments
    ---------
    
    ivecs_file_path : String specifying the path to the file containing
    i-vector files. i-vector files must be in Kaldi ark text format.
        
    Returns
    -------
    
    ivecs : Pandas DataFrame containing i-vectors.
    
    '''
    try:
        with codecs.open(ivecs_file_path, 'r') as ivecs_file:
            lines = ivecs_file.readlines()
    except Exception:
        print('Cannot open file for reading at path specified {}.'.
            format(ivecs_file_path))
        exit(1)
    lines = ' '.join([line.strip() for line in lines]).strip().split(']')
    lines = [line.strip().split() for line in lines if line.strip() != '']
    ivecs = pd.DataFrame([[line[0]] + [np.float64(x) for x in line[2:]] for
        line in lines])
    ivecs = ivecs.rename(columns={0: 'utt-id'})
    return ivecs


def read_ivecs_set(ivecs_dir_path, dialects):
    '''Reads i-vector files of the specified dialects from a directory
    
    Arguments
    ---------
    
    ivecs_dir_path : String specifying the path to the directory
    containing i-vector files
    
    dialects : A list of strings specifying dialects for which
    i-vectors will be read. The files in the directory must be named
    <dialect>.ivec, where <dialect> is the name of the dialect.
    
    Returns
    -------
    
    ivecs : Pandas DataFrame containing i-vectors and the corresponding
    dialects.
    
    '''
    ivecs = pd.DataFrame()
    for dialect in dialects:
        ivecs_file_path = ivecs_dir_path + os.sep + dialect + '.ivec'
        dialect_ivecs = read_ivectors_from_file(ivecs_file_path)
        # Add the dialect as the utterance label
        dialect_ivecs['dialect'] = dialect
        # Drop the utterance id column
        ivecs = ivecs.append(dialect_ivecs)
    return ivecs



