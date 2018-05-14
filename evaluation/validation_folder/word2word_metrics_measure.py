import pandas as pd
import numpy as np
import ast

from db.data.manager import get_golden_csv
from evaluation.validation_folder.evaluate import get_JPRF

if __name__ == '__main__':
    golden = get_golden_csv('new_golden.csv')
    data_frame = pd.read_csv('word2word_submission.csv', encoding='utf-8', )
    jaccard = []
    precision = []
    recall = []
    f_score = []

    for _, row in data_frame.iterrows():
        ideal_synset = golden[row.golden_id]['words']
        model_synset = set(ast.literal_eval(row.best))

        j, p, r, f = get_JPRF(ideal_synset, model_synset)
        jaccard.append(j)
        precision.append(p)
        recall.append(r)
        f_score.append(f)
    print('Mean jaccard', np.mean(jaccard))  # 0.5088472610410032
    print('Mean precision', np.mean(precision))  # 0.7041384171384172
    print('Mean recall', np.mean(recall))  # 0.687254134396406
    print('Mean f_score', np.mean(f_score))  # 0.6468006240394056
