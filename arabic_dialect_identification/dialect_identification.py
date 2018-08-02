import argparse
import dialect_enrollment
import numpy as np
import pandas as pd
import random
import tensorflow as tf
#from tensorflow import keras
import keras


dialects = ['EGY', 'GLF', 'LAV', 'MSA', 'NOR']


def parse_arguments():
    '''Parses command line arguments.

    Returns
    -------

    args : Dictionary of command line arguments.
    '''
    parser = argparse.ArgumentParser()
    train_ivecs_dir_path_help = ('Path to directory containing i-vectors of '
    'the training set.')
    dev_ivecs_dir_path_help = ('Path to directory containing i-vectors of the '
    'development set.')
    parser.add_argument('train_ivecs_dir_path', help=train_ivecs_dir_path_help,
        type=str)
    parser.add_argument('dev_ivecs_dir_path', help=dev_ivecs_dir_path_help,
        type=str)
    args = vars(parser.parse_args())
    return args


def euclidean_distance(y_true, cos_sim):
    '''Euclidean distance loss function.
    
    Arguments
    ---------
    
    y_true : 1-D NumPy array containing true labels.
    
    cos_sim : 1-D tensor containing cosine similarity scores.
    
    Returns
    -------
    
    euclid_dist : 0-D tensor of Euclidean distance between true labels
    and cosine similarity scores.
    '''
    euclid_dist = keras.backend.sum(keras.backend.square(y_true - 
        (1 - cos_sim)))
    return euclid_dist


def base_network(input_layer):
    '''Build the identical part constituting the Siamese NN branches.
    
    Arguments
    ---------
    
    input_layer : keras.layers.Input object.
    
    Returns
    -------
    
    fc_3 : keras.layers.Dense object with 200 nodes.
    '''
    if len(input_layer.shape) == 2:
        in_shape = input_layer.shape[1].value
    else:
        raise ValueError(('Expected shape (?,n). '
            'Found shape {} is not right.').format(input_layer.shape))
    input_reshaped = keras.layers.Reshape((in_shape,1))(input_layer)
    conv = keras.layers.Conv1D(filters=25, kernel_size=8,
                                 activation='relu',
                                padding='same')(input_reshaped)
    flat = keras.layers.Flatten()(conv)
    fc_1 = keras.layers.Dense(1500, activation='relu')(flat)
    fc_2 = keras.layers.Dense(600, activation='relu')(fc_1)
    fc_3 = keras.layers.Dense(200, activation='relu')(fc_2)
    return fc_3


def main():
    # Parse arguments
    args = parse_arguments()

    train_ivecs_dir_path = args['train_ivecs_dir_path']
    dev_ivecs_dir_path = args['dev_ivecs_dir_path']

    # Read i-vectors for training and test sets
    train_ivecs = dialect_enrollment.read_ivecs_set(train_ivecs_dir_path,
        dialects)
    dev_ivecs = dialect_enrollment.read_ivecs_set(dev_ivecs_dir_path,
        dialects)

    # Compute dialect enrollment
    de_model = dialect_enrollment.model(train_ivecs, dev_ivecs)

    # Create dataset by randomly choosing utterances and a dialect enrollment model, and deducing the corresponding dialect.
    #x_train = train_ivecs.sample(1000)
    #x_train = x_train.append(dev_ivecs.sample(50))
    x_train = train_ivecs.append(dev_ivecs)
    # Make sure all models have the same dimensionality
    model_lens = set(len(model) for model in de_model.values())
    assert len(model_lens) == 1
    # Form the other part of the training data from the model and append
    # it to the training data i-vectors
    de_model_df = pd.DataFrame([v.tolist() + [k] for k, v in
        de_model.items()], columns=list(range(model_lens.pop())) 
        + ['model_dialect'])
    x_train_model = de_model_df.sample(len(x_train), replace=True)
    x_train = x_train.reset_index(drop=True)
    x_train_model = x_train_model.reset_index(drop=True)
    y = pd.concat([x_train['dialect'],
        x_train_model['model_dialect']], axis=1)
    y['label'] = y.apply(lambda row: 1 if row['dialect'] ==
        row['model_dialect'] else 0, axis=1)
    y = y['label'].values
    x_train = x_train.drop('dialect', axis=1)
    x_train_model = x_train_model.drop('model_dialect', axis=1)

    # Create base network for the Siamese neural network
    input_1 = keras.layers.Input(shape=(400,))
    input_2 = keras.layers.Input(shape=(400,))
    base_net_1 = base_network(input_1)
    base_net_2 = base_network(input_2)
    # Create Siamese neural network
    merged = keras.layers.Dot(normalize=True, axes=1)(
        [base_net_1, base_net_2])
    model = keras.Model(inputs=[input_1, input_2], outputs=merged)
    model.compile(loss=euclidean_distance, optimizer='adam',
                metrics=['accuracy'])

    print('Printing model summary..')
    print(model.summary())

    # Setup a callback function to save the model every epoch
    model_file_path = 'model.{epoch:02d}.hdf5'
    checkpoint_callback = keras.callbacks.ModelCheckpoint(model_file_path,
        monitor='val_acc', verbose=1, save_best_only=True)
    #batch_progress_callback = keras.callbacks.LambdaCallback(
    #    on_batch_begin=lambda batch,logs: print('Batch {}'.format(batch)))

    # Train the network
    history = model.fit([x_train, x_train_model], y,
        epochs=100, batch_size=50, callbacks=[checkpoint_callback])

    print("Finished training.")


if __name__ == '__main__':
    main()
