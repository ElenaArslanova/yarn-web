import itertools
import abc
from typing import List, Tuple

import numpy as np

from db.alchemy import Alchemy
from models.metrics import general_metric


class Model(metaclass=abc.ABCMeta):
    def __init__(self, threshold: float, metric):
        """
        :param threshold: порог для метрики, число в [0, 1]
        :param metric: функция, вычисляющая схожесть двух слов и возвращающая число в [0, 1]
        вид функции - metric(a, b) -> float
        """
        self.__threshold = threshold
        self.__metric = metric
        self.__connection = Alchemy(path='../db/data.db')

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
    def _matrix_processing(self, matrix) -> List[int]:
        """
        функция для стратегии отбора слов, которые войдут в итоговый синсет
        :param matrix: матрица схожести определений слов на основании метрики
        :return: лист из int-ов - индексы тех слов из исходного синсета, которые являются синонимами на основании
        работы алгоритма
        """
        pass

    def clean(self, synset_id: int, missing_definitions_strategy: str = 'add_auto') -> Tuple[List, List]:
        """
        :param synset_id: id синсета в базе
        :param missing_definitions_strategy:
        определяет стратегию работы со словами, для которых нет определений в словаре
        :return: два листа: synset - слова, которые включены и dropped - лишние
        """
        response = self.__connection.get_synset_definitions(synset_id)

        if missing_definitions_strategy == 'add_auto':
            pairs = [(k, v) for k, v in response.items() if v is not None]
            print(pairs)
            auto = [k for k, v in response.items() if v is None]
            print([k for k, _ in pairs])
            matrix = self.__create_matrix(pairs)
            print(matrix)
        else:
            pass


class MajorityRowModel(Model):
    def _matrix_processing(self, matrix) -> List[int]:
        pass


if __name__ == '__main__':
    m = MajorityRowModel(0.4, general_metric)
    m.clean(1)
