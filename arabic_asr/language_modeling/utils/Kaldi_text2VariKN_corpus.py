import io
import argparse


def main():
    ''' Transforms Kaldi text file to corpus file ready for processing by VariKN
    '''
    # Parse command line arguments
    arg_parser = argparse.ArgumentParser(description=('Transform Kaldi text'
        'file to coprus ready for processing by VariKN.'))
    arg_parser.add_argument('kaldi_text', type=str,
        help=(('Path to the file'
            'containing the Kaldi text corpus.')))
    arg_parser.add_argument('output_corpus', type=str,
        help=(('Path to output'
            'file to save the corpus.')))
    args = vars(arg_parser.parse_args())

    path_to_text = args['kaldi_text']
    path_to_corpus = args['output_corpus']
    
    # Open the Kaldi text file and the output corpus as streams
    # (It maybe infeasible to perform offline processing in case of large
    # Kaldi text files)
    kaldi_text = io.open(path_to_text, 'r')
    output_corpus = io.open(path_to_corpus, 'w')
    
    # For each line in the Kaldi text, remove the utterance-id and add
    # VariKN sentence start and end symbols (<s> and </s> respectively)
    for line in kaldi_text:
        line = ' '.join(line.strip().split()[1:])
        line = '<s> ' + line + ' </s>\n'
        output_corpus.write(line)
    kaldi_text.close()
    output_corpus.close()


if __name__ == '__main__':
    main()
