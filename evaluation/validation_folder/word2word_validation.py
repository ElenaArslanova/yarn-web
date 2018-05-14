import tqdm

from db.data.manager import get_golden_csv, get_mapping
from evaluation.clusters import read_clusters
from models.metrics import jaccard_similarity
from models.word_to_word.model import WordToWord

import numpy as np
import pandas as pd

if __name__ == '__main__':
    model = WordToWord(threshold=0.45)  # лучший порог с валидации

    test_data = get_golden_csv('Test_set.csv')

    mapping = get_mapping('mapping.csv')
    clusters = read_clusters('../3to9.csv')

    golden_ids = []
    extracted_synsets = []
    scores = []

    for golden_id in tqdm.tqdm(test_data):
        ideal_synset = test_data[golden_id]['words']
        words = list(clusters[mapping[golden_id]]['words'])

        generated_synsets = model.extract_clusters(words)
        generated_scores = [jaccard_similarity(ideal_synset, set(extracted)) for extracted in generated_synsets]
        max_idx = np.argmax(generated_scores)

        golden_ids.append(golden_id)
        extracted_synsets.append(generated_synsets[max_idx])  # берем самый похожий
        scores.append(generated_scores[max_idx])

    print(np.mean(scores))

    pd.DataFrame({'golden_id': golden_ids, 'best': extracted_synsets}).to_csv('word2word_submission.csv')
