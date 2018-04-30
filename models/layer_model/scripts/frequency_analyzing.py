import pandas
import json
from tqdm import tqdm

from db.alchemy import Alchemy
from db.base import Word

if __name__ == '__main__':
    a = Alchemy('../../../db/data.db')
    session = a.get_session()
    frame = pandas.read_csv('yarn-synsets.csv', encoding='utf-8')
    #
    dictionary = set()
    words_with_no_defs = set()
    #
    synsets = frame.words
    for synset in synsets:
        dictionary.update(set(synset.split(';')))
    print(len(dictionary))

    for word in tqdm(dictionary):
        if session.query(Word).filter(Word.word == word).all():
            continue
        else:
            words_with_no_defs.add(word)

    print(len(dictionary))
    print(len(words_with_no_defs))

    with open('absent_words.json', 'w') as fp:
            json.dump(list(words_with_no_defs), fp)
    # report = json.load(open('absent_words.json'))
    # print(len([x for x in report if len(x.split()) == 1]))
    # print(len([x for x in report if len(x.split()) == 2]))
    # print(len(report))
    # for x in report[200:300]:
    #     print(x)

