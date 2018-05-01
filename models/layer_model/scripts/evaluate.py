from functools import partial

from db.data.manager import get_golden, load_alchemy
from models.layer_model.model import LayerModel
from models.metrics import general_metric, jacard_metric
from models.processing import remove_stop_words_tokens


def similarity(correct: set, model_prediction: set):
    return len(model_prediction.intersection(correct)) / len(model_prediction.union(correct))


if __name__ == '__main__':
    golden = get_golden('golden.txt', drop_bad_synsets=True, drop_unsure_words=True)

    metric = partial(general_metric, sim_metric=jacard_metric, processing=remove_stop_words_tokens)
    model = LayerModel(0.00001, metric)
    alchemy = load_alchemy('data.db')

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
