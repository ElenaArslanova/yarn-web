import json
import tqdm

import numpy as np

from db.base import Word
from models.layer_model.model import LayerModel
from models.layer_model.additional import Word2VecOrdering
from db.data.manager import get_golden, load_alchemy


def jaccard_similarity(correct: set, model_prediction: set):
    return len(model_prediction.intersection(correct)) / len(model_prediction.union(correct))


def process_tuning(correct_synset: set, model: LayerModel, thresholds: np.array, report: dict, definitions) -> float:
    for threshold in thresholds:
        model.set_fasttext_threshold(threshold)
        new_synsets = [set(x.words) for x in model.extract_new_synsets(definitions) if x.definitions]
        scores = [jaccard_similarity(correct_synset, generated_synset) for generated_synset in new_synsets]
        report[threshold]['scores'].append(max(scores))


if __name__ == '__main__':
    alchemy = load_alchemy('data.db')
    Word2VecOrdering.set_up()
    model = LayerModel(0.557, None)
    model.set_fasttext_definition_strategy('closest')

    thresholds = list(x / 100 for x in range(25, 100, 5))
    report = {}
    for threshold in thresholds:
        report[threshold] = {'threshold': threshold, 'scores': [], 'mean_score': 0}

    golden = get_golden('golden.txt', drop_bad_synsets=True, drop_unsure_words=True)
    clean_synsets_with_origin_ids = [(key, value) for key, value in golden.items() if value]

    for clean_synset, origin_ids in tqdm.tqdm(clean_synsets_with_origin_ids):
        concatenated_words = alchemy.get_concatenated_synsets_by_yarn_ids(origin_ids)
        ordered_words = Word2VecOrdering.order_words_sequence_using_average_sim(list(concatenated_words))
        definitions = alchemy.get_words_definitions(ordered_words)
        process_tuning(clean_synset, model, thresholds, report, definitions)
        print('FINISH {}'.format(clean_synset))

    for threshold in thresholds:
        report[threshold]['mean_score'] = np.mean(report[threshold]['scores'])

    with open('report_closest_sorted_search', 'w') as fp:
            json.dump(report, fp)

    # with open('report_closest_sorted_search') as fp:
    #     res = json.load(fp)
    # max_mean_score = max(res[t]['mean_score'] for t in res)
    # print(max_mean_score)
    #
    # for t in res:
    #     if res[t]['mean_score'] == max_mean_score:
    #         print(t)
    #
    # print(res['0.5']['mean_score'])

    # defs = alchemy.get_words_definitions(['пучина', 'бездна', 'пропасть'])
    # new_synsets = model.extract_new_synsets(defs)
    # for s in new_synsets:
    #     print('Новый синсет: {}'.format(', '.join(s.words)))
    #     if s.definitions:
    #         print('Определения:')
    #         for d in s.definitions:
    #             print('\t{}'.format(d))
    #     else:
    #         print('Нет определений в словаре')
    #     print('-------------------')