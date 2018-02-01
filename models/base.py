import itertools
import abc
from typing import List, Tuple

import numpy as np

from db.alchemy import Alchemy


class Model(metaclass=abc.ABCMeta):
    def __init__(self, threshold: float, metric):
        """
        :param threshold: порог для метрики, число в [0, 1]
        :param metric: функция, вычисляющая схожесть двух слов и возвращающая число в [0, 1]
        вид функции - metric(a, b) -> float
        """
        self.__threshold = threshold
        self.__metric = metric
        self.__connection = Alchemy()

    def __create_matrix(self, pair: Tuple[List[str], List[str]], multiple_meaning_strategy: str = 'closest'):
        """
        :param pair: кортеж из двух массивов: массив слов и массив определений
        :param multiple_meaning_strategy: что делать с многозначными словами, какое определение выбирать.
        :return: матрицу, где [i, j] - похожесть i-го определения слова на j-ое определение
        """
        if multiple_meaning_strategy != 'closest':
            pass
        else:
            scorer = self.strict_similarity

        words, definitions = pair
        length = len(words)
        matrix = np.zeros((length, length))
        for i in range(length):
            for j in range(length):
                if i == j or matrix[i, j] != 0:
                    continue

                first_def = [definitions[i]] if type(definitions[i]) != list else definitions[i]
                second_def = [definitions[j]] if type(definitions[j]) != list else definitions[j]
                matrix[i, j] = scorer(first_def, second_def)
                matrix[j, i] = matrix[i, j]
                
        return matrix

    def strict_similarity(self, first, second) -> float:
        """
        :param first: лист из определений
        :param second: как и first
        :return: возвращает самую большую схожесть между определениями по метрике из first и second
        """
        return max(map(lambda *args: self.__metric(*args), itertools.permutations(first, second)))

    @abc.abstractmethod
    def _matrix_processing(self, matrix) -> List[int]:
        """
        функция для стратегии отбора слов, которые войдут в итоговый синсет
        :param matrix: матрица схожести определений слов на основании метрики
        :return: лист из int-ов - индексы тех слов из исходного синсета, которые являются синонимами на основании
        работы алгоритма
        """
        pass

    def clean(self, synset_id: int) -> Tuple[List, List]:
        """
        :param synset_id: id синсета в базе
        :return: два листа: synset - слова, которые включены и dropped - лишние
        """
        pass
