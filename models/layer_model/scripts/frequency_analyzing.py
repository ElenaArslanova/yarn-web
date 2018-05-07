import json
import tqdm
import os
from typing import List

from db.base import Word, WordDefinitionRelation, Definition
from db.data.manager import load_alchemy, read_pandas, get_golden, load_json_file


def add_absent_words_from_dictionary(absent_words: List[str], dict_path: str):
    """
    Добавляет слова из absent_words в базу
    :param absent_words: список недостающих слов
    :param dict_path: путь до словаря
    :return:
    """
    a = load_alchemy('data.db')
    session = a.get_session()
    session_counter = 0
    absent_words = set(absent_words)
    added_word_id = {}
    with open(dict_path) as f:
        for line in tqdm.tqdm(f):
            if session_counter == 100:
                session.commit()
                session_counter = 0
            dict_entry = json.loads(line)
            if 'definition' in dict_entry and dict_entry['word']:
                word_entry = dict_entry['word'][0]
                if word_entry in absent_words:
                    definitions = [Definition(d) for d in dict_entry['definition']]
                    if word_entry not in added_word_id:
                        word = Word(word_entry, dict_entry['POS'])
                        session.add(word)
                        session.flush()
                        word_id = word.id
                        added_word_id[word_entry] = word.id
                    else:
                        word_id = added_word_id[word_entry]
                    for d in definitions:
                        session.add(d)
                        session.flush()
                        session.add(WordDefinitionRelation(word_id, d.id))
                    session_counter += 1
    session.commit()
    return list(added_word_id.keys())


def add_absent_words_from_all_dictionaries():
    dicts = ['ru.wikt', 'mas', 'ushakov', 'bts', 'ruTes', 'ozhshv', 'babenko', 'yarn', 'efremova']
    dict_paths = {d: 'dicts/{}_final.json'.format(d) for d in dicts[1:]}
    dict_absent = {d: '{}_absent.json'.format(d) for d in dicts}
    for i, d in enumerate(dicts[1:]):
        with open(dict_absent[dicts[i]]) as f:
            absent_words = json.load(f)
        print('----------------------------------')
        print('Missing {} words'.format(len(absent_words)))
        print('Adding {}'.format(dict_paths[d]))
        added = add_absent_words_from_dictionary(absent_words, dict_paths[d])
        print('{} words added'.format(len(added)))
        new_absent = set(absent_words) - set(added)
        with open(dict_absent[dicts[i+1]], 'w') as f:
            json.dump(list(new_absent), f)
        print('Now missing {} words'.format(len(new_absent)))


def test_all_available_dictionaries(absent_words):
    absent_words = set(absent_words)
    for dict_path in os.listdir('dicts'):
        added_words = set()
        if not dict_path.startswith('.'):
            with open(os.path.join('dicts',dict_path)) as f:
                for line in f:
                    dict_entry = json.loads(line)
                    if 'definition' in dict_entry and dict_entry['word']:
                        word_entry = dict_entry['word'][0]
                        if word_entry in absent_words:
                            added_words.add(word_entry)
            print('-----------------------')
            print('Testing {}, found {} absent words'.format(dict_path, len(added_words)))


def analyze_golden():
    alchemy = load_alchemy('data.db')
    golden = get_golden('golden.txt', drop_bad_synsets=True, drop_unsure_words=True)
    absent_words = set(load_json_file('yarn_absent.json'))
    clean_synsets_with_origin_ids = [(key, value) for key, value in golden.items() if value]
    golden_absent = set()
    collocations = set()
    for clean_synset, origin_ids in clean_synsets_with_origin_ids:
        concatenated_words = alchemy.get_concatenated_synsets_by_yarn_ids(origin_ids)
        for word in concatenated_words:
            if len(word.split()) > 1:
                collocations.add(word)
            elif word in absent_words:
                golden_absent.add(word)

    print('Missing {} words'.format(len(golden_absent)))
    print('{} collocations found'.format(len(collocations)))

    with open('golden_absent.json', 'w') as f:
        json.dump(list(golden_absent), f)
    with open('golden_collocations.json', 'w') as f:
        json.dump(list(collocations), f)


def find_absent_words():
    a = load_alchemy('data.db')
    session = a.get_session()
    frame = read_pandas('yarn-synsets.csv')

    dictionary = set()
    words_with_no_defs = set()

    synsets = frame.words
    for synset in synsets:
        dictionary.update(set(synset.split(';')))
    print(len(dictionary))

    for word in tqdm.tqdm(dictionary):
        if session.query(Word).filter(Word.word == word).all():
            continue
        else:
            words_with_no_defs.add(word)

    print(len(dictionary))
    print(len(words_with_no_defs))

    with open('absent_words.json', 'w') as fp:
        json.dump(list(words_with_no_defs), fp)



if __name__ == '__main__':
    analyze_golden()


    # add_absent_words_from_all_dictionaries()

    # test_all_available_dictionaries(absent_words)

    # with open('yarn_absent.json') as f:
    #     absent_words = json.load(f)
    #
    # for w in absent_words:
    #     if len(w.split(' ')) == 1:
    #         print(w)

