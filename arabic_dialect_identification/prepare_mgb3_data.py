import codecs
import os


def append_with_annotator_prefix(file_path, agg_file, annotator):
    with codecs.open(file_path, 'r') as f:
            lines = f.readlines()
    lines = [annotator + '_' + line for line in lines]
    agg_file.write(''.join(lines))


def get_wav_ids_from_file(file_path):
    with codecs.open(file_path, 'r') as f:
            lines = f.readlines()
    wav_ids = set([line.strip().split()[1] for line in lines])
    return wav_ids


def make_utt2spk(file_path, dst_file):
    with codecs.open(file_path, 'r') as f:
            lines = f.readlines()
    seg_ids = [line.strip().split()[0] for line in lines]
    utt2spk_output = '\n'.join(['{seg_id} {seg_id}'.format(seg_id=seg_id)
        for seg_id in seg_ids])
    dst_file.write(utt2spk_output + '\n')


def main():
    base_dir = ''
    data_set_names = ['adapt.20170322',  'dev.20170322']
    annotators = ['Alaa', 'Ali', 'Mohamed', 'Omar']

    agg_dir = os.path.join(base_dir, 'aggregated_data')
    if not os.path.isdir(agg_dir):
        os.makedirs(agg_dir)
    data_set_names = ['adapt.20170322',  'dev.20170322']
    for data_set_name in data_set_names:
        data_set_dir = os.path.join(agg_dir, data_set_name)
        if not os.path.isdir(data_set_dir):
            os.makedirs(data_set_dir)

    for data_set_name in data_set_names:
        wav_ids = set()
        segments_agg_file_path = os.path.join(agg_dir, data_set_name,
                                            'segments')
        text_agg_file_path = os.path.join(agg_dir, data_set_name, 'text')
        wav_file_path = os.path.join(agg_dir, data_set_name, 'wav.scp')
        utt2spk_file_path = os.path.join(agg_dir, data_set_name, 'utt2spk')
        segments_agg_file = codecs.open(segments_agg_file_path, 'w')
        text_agg_file = codecs.open(text_agg_file_path, 'w')
        utt2spk_file = codecs.open(utt2spk_file_path, 'w')
        for annotator in annotators:
            # Add segments and text data to aggregated files with annotator
            # name as a prefix to segment id's
            # Make a set of utterance id's
            data_dir = os.path.join(base_dir, data_set_name, annotator)
            text_file_path = os.path.join(data_dir, 'text_noverlap.bw')
            segments_file_path = os.path.join(data_dir, 'segments')
            append_with_annotator_prefix(text_file_path, text_agg_file,
                annotator)
            append_with_annotator_prefix(segments_file_path,
                segments_agg_file, annotator)
            new_wav_ids = get_wav_ids_from_file(segments_file_path)
            wav_ids.update(new_wav_ids)
        make_utt2spk(segments_agg_file_path, utt2spk_file)
        # Ouput wav.scp
        with open(wav_file_path, 'w') as wav_file:
            wav_file.write(''.join([wav_id + ' ' + wav_id + '.wav\n' for
                                    wav_id in wav_ids]))
        # Close files
        segments_agg_file.close()
        text_agg_file.close()
        wav_file.close()
        utt2spk_file.close()

if __name__ == '__main__':
    main()
