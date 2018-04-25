import json

import numpy as np

from db.alchemy import Alchemy
from models.layer_model.model import LayerModel
from models.layer_model.scripts.utils import get_golden


def jaccard_similarity(correct: set, model_prediction: set):
    return len(model_prediction.intersection(correct)) / len(model_prediction.union(correct))


def process_tuning(correct_synset: set, model: LayerModel, thresholds: np.array, report: dict, definitions) -> float:
    for threshold in thresholds:
        model.set_fasttext_threshold(threshold)
        new_synsets = [set(x.words) for x in model.extract_new_synsets(definitions) if x.definitions]
        scores = [jaccard_similarity(correct_synset, generated_synset) for generated_synset in new_synsets]
        report[threshold]['scores'].append(max(scores))


if __name__ == '__main__':
    alchemy = Alchemy('../../../db/data.db')
    model = LayerModel(0.557, None)
    thresholds = list(x / 100 for x in range(25, 100, 5))
    report = {}
    for threshold in thresholds:
        report[threshold] = {'threshold': threshold, 'scores': [], 'mean_score': 0}

    golden = get_golden('../golden.txt', drop_bad_synsets=True, drop_unsure_words=True)
    clean_synsets_with_origin_ids = [(key, value) for key, value in golden.items() if value]

    for clean_synset, origin_ids in clean_synsets_with_origin_ids[1:2]:
        concatenated_words = alchemy.get_concatenated_synsets_by_yarn_ids(origin_ids)
        definitions = alchemy.get_words_definitions(concatenated_words)

        process_tuning(clean_synset, model, thresholds, report, definitions)

    for threshold in thresholds:
        report[threshold]['mean_score'] = np.mean(report[threshold]['scores'])

    with open('report.json', 'w') as fp:
            json.dump(report, fp)
