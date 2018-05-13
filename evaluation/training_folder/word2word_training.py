import json

import tqdm

from db.data.manager import get_golden_csv, read_pandas, get_mapping
from evaluation.clusters import read_clusters
from models.metrics import jaccard_similarity
from models.word_to_word.model import WordToWord

import numpy as np

if __name__ == '__main__':
    model = WordToWord()
    thresholds = list(x / 100 for x in range(25, 100, 5))
    training_data = get_golden_csv('training_set.csv')

    mapping = get_mapping('mapping.csv')
    clusters = read_clusters('../3to9.csv')

    results = {}
    for threshold in tqdm.tqdm(thresholds):
        temp_results = []
        model.set_threshold(threshold)
        for golden_id in training_data:
            ideal_synset = training_data[golden_id]['words']
            words = clusters[mapping[golden_id]]['words']

            generated_synsets = model.extract_clusters(words)
            scores = [jaccard_similarity(ideal_synset, set(synset)) for synset in generated_synsets]
            temp_results.append(max(scores))
            print(max(scores))
        results[threshold] = np.mean(temp_results)

    with open('report.json', 'w') as fp:
            json.dump(results, fp)