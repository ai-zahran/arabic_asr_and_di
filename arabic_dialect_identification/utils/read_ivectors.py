import codecs
import numpy as np
import os
import pandas as pd


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
        # Strip files train and dev i-vector files, since the delimiter is the
        # space character.
        try:
            with codecs.open(ivecs_file_path, 'r') as f:
                lines = f.readlines()
        except Exception:
            print('Cannot open file for reading at path specified {}.'.
                format(ivecs_file_path))
            exit(1)
        lines = [line.strip().split() for line in lines]
        lines = [[np.float64(x) for x in line[1:]] for line in lines]
        dialect_ivecs = pd.DataFrame(lines)
        # Add the dialect as the utterance label
        dialect_ivecs['dialect'] = dialect
        # Drop the utterance id column
        ivecs = ivecs.append(dialect_ivecs)
    return ivecs

