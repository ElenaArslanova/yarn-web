from functools import partial

from db.alchemy import Alchemy
from models.base import MajorityRowModel
from models.layer_model.model import LayerModel
from models.metrics import general_metric, jacard_with_word_influence, jacard_metric
from models.processing import remove_stop_words_tokens


def get_golden(filename, drop_bad_synsets=True, drop_unsure_words=True):
    import re
    with open(filename, 'r', encoding='utf-8') as f:
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


def similarity(correct: set, model_prediction: set):
    return len(model_prediction.intersection(correct)) / len(model_prediction.union(correct))


if __name__ == '__main__':
    golden = get_golden('golden.txt', drop_bad_synsets=True, drop_unsure_words=True)

    metric = partial(general_metric, sim_metric=jacard_metric, processing=remove_stop_words_tokens)
    model = LayerModel(0.00001, metric)
    alchemy = Alchemy(path='../../db/data.db')

    scores = []
    for key, value in golden.items():
        print(value)
        concatenated_words = alchemy.get_concatenated_synsets_by_yarn_ids(value)
        definitions = alchemy.get_words_definitions(concatenated_words)
        new_synsets = model.extract_new_synsets(definitions)
        print()
        print(concatenated_words)
        for s in new_synsets:
            print('Новый синсет: {}'.format(', '.join(s.words)))
            if s.definitions:
                print('Определения:')
                for d in s.definitions:
                    print('\t{}'.format(d))
            else:
                print('Нет определений в словаре')
            print('-------------------')
    #     clean, dropped = m.clean(definitions)[0]
    #     score = similarity(key, set(clean))
    #     scores.append(score)
    # print('Mean score: {}'.format(np.mean(scores)))