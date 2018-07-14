import json
import os
import csv
import pandas as pd
from gensim.models import FastText, Word2Vec, KeyedVectors

from db.alchemy import Alchemy

__FASTTEXT_MODEL = None
__WORD2VEC_MODEL = None


def load_text_file(file_name: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read()


def load_json_file(file_name: str):
    return json.load(open(os.path.join(os.path.dirname(__file__), file_name)))


def load_fasttext_bin(model_path: str):
    global __FASTTEXT_MODEL

    if __FASTTEXT_MODEL:
        return __FASTTEXT_MODEL

    __FASTTEXT_MODEL = FastText.load(os.path.join(os.path.dirname(__file__), model_path))
    return __FASTTEXT_MODEL


def load_word2vec_bin(model_path: str):
    # now using fasttext, not word2vec
    # для wor2vec должно быть так:
    # return KeyedVectors.load_word2vec_format(os.path.join(os.path.dirname(__file__), model_path), binary=False)
    # сейчас так:
    return load_fasttext_bin(model_path)


def load_alchemy(db_path: str) -> Alchemy:
    return Alchemy(os.path.join(os.path.dirname(__file__), db_path))


def read_pandas(path_file: str, sep=';') -> pd.DataFrame:
    return pd.read_csv(os.path.join(os.path.dirname(__file__), path_file), encoding='utf-8', sep=sep)


def get_golden(filename, drop_bad_synsets=True, drop_unsure_words=True):
    import re
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        raw = f.read()

    raw = raw.strip()

    if drop_bad_synsets:
        raw = re.sub(r'#\d+\n?', '', raw)
    else:
        raw = raw.replace('#', '')

    if drop_unsure_words:
        raw = re.sub(r'\?\w+, |, \?\w+', '', raw)
    else:
        raw = raw.replace('?', '')

    clusters = raw.split('\n\n')
    golden = {}
    for cluster in clusters:
        words, *sIDs = cluster.split('\n')
        words = frozenset(words.split(', '))
        sIDs = set(int(sID) for sID in sIDs if sID)
        golden[words] = sIDs
    return golden


def get_golden_csv(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', fieldnames=['index', 'synset_ids', 'words'])
        golden = {}
        for row in reader:
            index = row['index']
            golden[index] = {}
            golden[index]['synset_ids'] = set(
                [int(s_id) for s_id in row['synset_ids'].split(',')])
            golden[index]['words'] = frozenset(row['words'].split(','))
        return golden


def get_mapping(mapping_file, mapping_dir='mappings'):
    with open(os.path.join(os.path.dirname(__file__), mapping_dir, mapping_file)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        return {row['golden_id']: int(row['cluster_id']) for row in reader}


if __name__ == '__main__':
    print(get_mapping('mapping.csv'))
