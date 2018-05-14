import tqdm

from db.data.manager import get_golden_csv, get_mapping, load_alchemy
from evaluation.clusters import read_clusters
from models.metrics import jaccard_similarity
from models.layer_model.model import LayerModel
from models.layer_model.additional import Word2VecOrdering

import numpy as np
import pandas as pd

if __name__ == '__main__':
    alchemy = load_alchemy('data.db')
    Word2VecOrdering.set_up()
    model = LayerModel(0.557, None)
    model.set_fasttext_definition_strategy('average')
    model.set_fasttext_threshold(0.55)  # лучший порог с валидации

    test_data = get_golden_csv('Test_set.csv')

    mapping = get_mapping('mapping.csv')
    clusters = read_clusters('../3to9.csv')

    golden_ids = []
    extracted_synsets = []
    scores = []

    for golden_id in tqdm.tqdm(test_data):
        ideal_synset = test_data[golden_id]['words']
        words = list(clusters[mapping[golden_id]]['words'])

        ordered_words = Word2VecOrdering.order_words_sequence_using_average_sim(words)
        definitions = alchemy.get_words_definitions(ordered_words)

        generated_synsets = model.extract_new_synsets(definitions)
        generated_scores = [jaccard_similarity(ideal_synset, set(extracted.words)) for extracted in generated_synsets]
        max_idx = np.argmax(generated_scores)

        golden_ids.append(golden_id)
        extracted_synsets.append(generated_synsets[max_idx].words)  # берем самый похожий
        scores.append(generated_scores[max_idx])

    print(np.mean(scores))

    pd.DataFrame({'golden_id': golden_ids, 'best': extracted_synsets}).to_csv('word2defs_average_submission.csv')
