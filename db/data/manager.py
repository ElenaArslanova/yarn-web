import json
import os
import pandas as pd
from gensim.models import FastText

from db.alchemy import Alchemy


def load_text_file(file_name: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read()


def load_json_file(file_name: str):
    return json.load(open(os.path.join(os.path.dirname(__file__), file_name)))


def load_fasttext_bin(model_path: str):
    return FastText.load(os.path.join(os.path.dirname(__file__), model_path))


def load_alchemy(db_path: str) -> Alchemy:
    return Alchemy(os.path.join(os.path.dirname(__file__), db_path))


def read_pandas(path_file: str) -> Alchemy:
    return pd.read_csv(os.path.join(os.path.dirname(__file__), path_file), encoding='utf-8')


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
