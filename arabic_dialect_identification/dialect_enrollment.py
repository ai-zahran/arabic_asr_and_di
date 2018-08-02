
# coding: utf-8

import argparse
import codecs
import os
import pandas as pd
from utils.read_ivectors import read_ivecs_set


dialects = ['EGY', 'GLF', 'LAV', 'MSA', 'NOR']
INTERP_PARAM = 0.83


def parse_arguments():
    '''Parses command line arguments.

    Returns
    -------

    args : Dictionary of command line arguments.
    '''
    train_ivecs_dir_path_help=('Path to directory containing training set '
        'i-vectors.')
    dev_ivecs_dir_path_help=('Path to directory containing development set '
        'i-vectors.')
    save_to_help='Path to save dialect enrollment.'
    arg_parser = argparse.ArgumentParser(
        description=('Calculate dialect enrollment for '
        'a group of i-vectors.'),
        epilog=('e.g.: python dialect_enrollment.py /path/to/train_ivecs '
        '/path/to/dev_ivecs'))
    arg_parser.add_argument('train_ivecs_dir_path', type='str',
        help=train_ivecs_dir_path_help)
    arg_parser.add_argument('dev_ivecs_dir_path', type='str',
        help=dev_ivecs_dir_path_help)
    arg_parser.add_argument('--save-to', dest='save_to', type=str,
        help=save_to_help)
    args = vars(arg_parser.parse_args())
    return args


def get_dial_model(ivec_df):
    ''' Computes i-vector dialect model.
    
    Arguments
    ---------
    
    ivec_df : Pandas DataFrame of i-vectors.
    
    Returns
    -------
    
    model : Pandas Series containing the dialect model.
    '''
    model = ivec_df.sum(axis=0) / ivec_df.shape[0]
    return model


def get_interp_model(train_model, dev_model, interp_param=INTERP_PARAM):
    '''Computes the interpolated dialect model from training and dev models
    
    Arguments
    ---------
    
    train_model : Pandas Series containing i-vector dialect model for the
    training set.
    
    dev_model : Pandas Series containing i-vector dialect model for the
    development set.
    
    interp_param : Float specifying the interpolation parameter.
    
    Returns
    -------
    
    interp_model: Numpy array containing the interpolated i-vector model.
    '''
    interp_model = (1 - interp_param) * train_model + interp_param * dev_model
    return interp_model.values


def model(train_ivecs, dev_ivecs, interp_param=INTERP_PARAM):
    '''Compute interpolated i-vector dialect model given utterance i-vectors
    
    Arguments
    ---------

    train_ivecs : Pandas DataFrame of i-vectors for the training set with
    corresponding dialects.

    dev_ivecs : Pandas DataFrame of i-vectors for the development set with
    corresponding dialects

    interp_param : Float specifying the interpolation parameter. Default value
    is 0.8.
    
    Returns
    -------
    
    interp_ivec_dial_model : Dictionary representing dialect models for the 
    different dialects. Keys are strings representing the name of the dialect,
    and values are Numpy array containing the interpolated i-vector model.
    '''
    # Compute i-vector dialect models for training and development sets of
    # different dialects
    dial_models = dict()
    for dialect in dialects:
        train_dialect_ivecs = train_ivecs.loc[train_ivecs['dialect'] ==
                                            dialect]
        dev_dialect_ivecs = dev_ivecs.loc[dev_ivecs['dialect'] == dialect]
        train_model = get_dial_model(train_dialect_ivecs.drop(
            columns='dialect'))
        dev_model = get_dial_model(dev_dialect_ivecs.drop(
            columns='dialect'))
        dial_models[dialect] = {'train_model': train_model, 'dev_model':
                                dev_model}
    # Compute interpolated i-vector dialect models for each dialect
    interp_ivec_dial_model = {dialect: get_interp_model(
        models['train_model'], models['dev_model'], INTERP_PARAM) for dialect,
            models in dial_models.items()}
    return interp_ivec_dial_model


def main():
    # Read training and test i-vectors
    args = parse_arguments()
    train_ivecs_dir_path = args['train_ivecs_dir_path']
    dev_ivecs_dir_path = args['dev_ivecs_dir_path']
    model_file_path = args['save_to']
    train_ivecs = read_ivecs_set(train_ivecs_dir_path, dialects)
    dev_ivecs = read_ivecs_set(dev_ivecs_dir_path, dialects)
    # Compute dialect enrollment for each dialect
    de_model = model(train_ivecs, dev_ivecs)
    # Save model if specified
    if model_file_path is not None:
        output = '\n'.join([d + ' '.join([str(x) for x in m]) for d, m in 
                            de_model.items()])
        try:
            with codecs.open(model_file_path, 'w') as model_file:
                model_file.write(output)
        except Exception:
            print('Cannot open file for writing in the specified path: {}.'
                .format(model_file_path))
            exit(1)
    return 0


if __name__ == '__main__':
    main()
