import itertools
import abc
from collections import OrderedDict
from typing import List, Tuple, Dict
from functools import partial

import numpy as np
import pandas as pd

from db.alchemy import Alchemy
from models.metrics import general_metric, jacard_with_word_influence
from models.processing import remove_stop_words_tokens
from models.utils import results_as_dict


class Model(metaclass=abc.ABCMeta):
    def __init__(self, threshold: float, metric):
        """
        :param threshold: порог для метрики, число в [0, 1]
        :param metric: функция, вычисляющая схожесть двух слов и возвращающая число в [0, 1]
        вид функции - metric(a, b) -> float
        """
        self._threshold = threshold
        self.__metric = metric

    def __create_matrix(self, pair: List[Tuple[str, List[str]]], multiple_meaning_strategy: str = 'closest'):
        """
        :param pair: лист из кортежей вида: слово - лист определений
        :param multiple_meaning_strategy: что делать с многозначными словами, какое определение выбирать.
        :return: матрицу, где [i, j] - похожесть i-го определения слова на j-ое определение
        """
        if multiple_meaning_strategy != 'closest':
            pass
        else:
            scorer = self.strict_similarity

        length = len(pair)
        matrix = np.zeros((length, length))
        viewed_elements = np.zeros((length, length), dtype=bool)

        for i in range(length):
            for j in range(length):
                if i == j or viewed_elements[i, j]:
                    continue

                matrix[i, j] = matrix[j, i] = scorer(pair[i], pair[j])
                viewed_elements[i, j], viewed_elements[i, j] = True, True

        return matrix

    def strict_similarity(self, first: Tuple[str, List[str]], second: Tuple[str, List[str]]) -> float:
        """
        :param first: кортеж из слова и листа определений к нему
        :param second: как и first
        :return: возвращает самую большую схожесть между определениями по метрике из first и second
        """
        w1, ds1 = first
        w2, ds2 = second
        return max(map(lambda x: self.__metric(w1, w2, x[0], x[1]), itertools.product(ds1, ds2)))

    @abc.abstractmethod
    def _matrix_processing(self, matrix) -> np.ndarray:
        """
        функция для стратегии отбора слов, которые войдут в итоговый синсет
        :param matrix: матрица схожести определений слов на основании метрики
        :return: лист из int-ов - индексы тех слов из исходного синсета, которые являются синонимами на основании
        работы алгоритма
        """
        pass

    def clean(self, synset_definitions: List[Dict[str, List[str]]], missing_definitions_strategy: str = 'add_auto') \
            -> List[Tuple[List, List]]:
        """
        :param synset_definitions:
        :param missing_definitions_strategy:
        определяет стратегию работы со словами, для которых нет определений в словаре
        :return: два листа: synset - слова, которые включены и dropped - лишние
        """
        pairs = map(lambda x: [(k, v) for k, v in x.items()], synset_definitions)
        if missing_definitions_strategy == 'add_auto':
            return list(map(lambda synset: self.__add_auto_strategy(synset), pairs))
        else:
            pass
            # TODO

    def __add_auto_strategy(self, def_pairs: List[Tuple[str, List[str]]]) \
            -> Tuple[List[str], List[str]]:
        """
        реализует повеение по умолчанию для тех слов, которых нет в словаре. Такие слова автоматически будут добавлены
        в итоговый синсет.
        :param def_pairs: лист из кортежей вида (w, List[d]), w - слово, List[d] - лист определений для w,
        если определений нет - , то вместо List[d] для слова w в кортеже будет None
        :return: возвращает два листа: synset - корректные синонимы и dropped - отфильтрованные алгоритмом
        """
        if len(def_pairs) == 1:
            return [def_pairs[0][0]], []
        pairs = [(k, v) for k, v in def_pairs if v is not None]
        auto = [k for k, v in def_pairs if v is None]
        matrix = self.__create_matrix(pairs)
        result_indexes = self._matrix_processing(matrix)
        synset = [pairs[i][0] for i in result_indexes]
        synset.extend(auto)
        return synset, list(set(k for k, _ in pairs) - set(synset))


class MajorityRowModel(Model):
    def _matrix_processing(self, matrix) -> np.ndarray:
        rows, _ = np.where(matrix >= self._threshold)
        return np.unique(rows)


if __name__ == '__main__':
    metric = partial(general_metric, sim_metric=jacard_with_word_influence, processing=remove_stop_words_tokens)
    m = MajorityRowModel(0.4, metric)
    alchemy = Alchemy(path='../db/data.db')
    yarn_ids, synset_definitions = alchemy.get_synsets_definitions((500, 505))
    answers = m.clean(synset_definitions)
    print(answers)
    # filtered = []
    # dropped = []
    # source = []
    # id = []
    # for idx, answer in zip(yarn_ids, answers):
    #     clean, dirty = answer
    #     filtered.append(';'.join(clean))
    #     dropped.append(';'.join(dirty))
    #     clean.extend(dirty)
    #     source.append(';'.join(clean))
    #     id.append(idx)
    # frame = pd.DataFrame(OrderedDict({'yarn_id': id, 'исходный синсет': source, 'отфильтрованный': filtered,
    #                                   'остальное': dropped}))
    # frame.to_csv('batch.csv', encoding='utf-8')
    print('-------')
    print(results_as_dict(yarn_ids, answers))
