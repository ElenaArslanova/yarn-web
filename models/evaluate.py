from functools import partial

from db.alchemy import Alchemy
from db.data.manager import get_golden
from models.base import MajorityRowModel
from models.metrics import general_metric, jacard_with_word_influence
from models.processing import remove_stop_words_tokens




def similarity(correct: set, model_prediction: set):
    return len(model_prediction.intersection(correct)) / len(model_prediction.union(correct))


if __name__ == '__main__':
    import numpy as np
    golden = get_golden('golden.txt', drop_bad_synsets=True, drop_unsure_words=True)

    metric = partial(general_metric, sim_metric=jacard_with_word_influence, processing=remove_stop_words_tokens)
    m = MajorityRowModel(0.37, metric)
    alchemy = Alchemy(path='../db/data.db')
    # yarn_id, definitions = alchemy.get_synset_definitions(1)
    # clean, dropped = m.clean(definitions)[0]
    scores = []
    for key, value in golden.items():
        concatenated_words = alchemy.get_concatenated_synsets_by_yarn_ids(value)
        definitions = [alchemy.get_words_definitions(concatenated_words)]
        clean, dropped = m.clean(definitions)[0]
        score = similarity(key, set(clean))
        scores.append(score)
    print('Mean score: {}'.format(np.mean(scores)))