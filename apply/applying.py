import random
import os
from typing import List

import pandas as pd
import tqdm

from apply.structures import DefDict, ClustersHolder
from models.layer_model.additional import Word2VecOrdering
from models.layer_model.model import LayerModel


if __name__ == '__main__':
    model = LayerModel(0.45, None)
    model.set_fasttext_definition_strategy('average')
    print('Модель загружена')

    read_count = 0  # сколько всего прочитано строк
    d = DefDict()  # словарь

    # ch = ClustersHolder()  # лежат все кластеры
    processed = {'yarn_id': [], 'words': [], 'def_ids': []}

    chunk_size = 1000  # сколько синсевто будет считано в одну тиреацию
    from_start = True
    # TODO нужно учесть, что мы сохраняем данные и если что-то упадет, то заново все считывать не надо

    # после каждой итерации будет производиться сохранение результата, чтобы если что-то упало, это можно было бы не
    # перечитывать
    while read_count < 70468:  # столько синсетов всего
        print(read_count)
        sub_frame_reader = pd.read_csv('yarn-synsets.csv', skiprows=read_count, chunksize=chunk_size)
        for sub_frame in sub_frame_reader:
            for _, row in tqdm.tqdm(sub_frame.iterrows()):
                words = row.words.split(';')
                ordered_words = Word2VecOrdering.order_words_sequence_using_average_sim(words)

                model_input = d.get_synset_definitions(ordered_words)  # словарь вида word: List[str] - список определений
                model_output = model.extract_new_synsets(model_input)

                for new_synset in model_output:
                    processed['yarn_id'].append(row.id)
                    processed['words'].append(';'.join(new_synset.words))
                    if new_synset.definitions:
                        processed['def_ids'].append(';'.join(str(d.id) for d in new_synset.definitions))
                    else:
                        processed['def_ids'].append('')
                # ch.process_synsets(model_output)

            print('Прочитано строк в итерации: {}'.format(sub_frame.shape[0]))
            last_pointer = read_count
            read_count += sub_frame.shape[0]

            pd.DataFrame(processed).to_csv(os.path.join('new_synsets', 'new_synsets_{}_{}.csv'.format(last_pointer, read_count)))
            processed = {'yarn_id': [], 'words': [], 'def_ids': []}
            print('Сохранен результат текущей итерации в файл {}'.format('new_synsets_{}_{}.csv'.format(last_pointer, read_count)))
        # break

        # ch.save_clusters_to_frame('clusters{}_{}.csv'.format(last_pointer, read_count))
        # print('Сохранен результат текущей итерации в файл {}'.format('clusters{}_{}.csv'.format(last_pointer, read_count)))
