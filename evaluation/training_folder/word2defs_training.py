import json

import tqdm

from db.data.manager import get_golden_csv, get_mapping, load_alchemy
from evaluation.clusters import read_clusters
from models.layer_model.additional import Word2VecOrdering
from models.metrics import jaccard_similarity
from models.layer_model.model import LayerModel

import numpy as np

if __name__ == '__main__':
    alchemy = load_alchemy('data.db')
    Word2VecOrdering.set_up()
    model = LayerModel(0.557, None)
    model.set_fasttext_definition_strategy('average')

    thresholds = list(x / 100 for x in range(25, 100, 5))
    training_data = get_golden_csv('training_set.csv')

    mapping = get_mapping('mapping.csv')
    clusters = read_clusters('../3to9.csv')

    results = {}
    for threshold in tqdm.tqdm(thresholds):
        temp_results = []
        model.set_fasttext_threshold(threshold)
        for golden_id in training_data:
            ideal_synset = training_data[golden_id]['words']
            words = clusters[mapping[golden_id]]['words']

            ordered_words = Word2VecOrdering.order_words_sequence_using_average_sim(list(words))
            definitions = alchemy.get_words_definitions(ordered_words)

            generated_synsets = model.extract_new_synsets(definitions)
            scores = [jaccard_similarity(ideal_synset, set(synset.words)) for synset in generated_synsets]

            temp_results.append(max(scores))

        results[threshold] = np.mean(temp_results)

    with open('word2defs_average_report.json', 'w') as fp:
            json.dump(results, fp)