from itertools import combinations
from typing import List

import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

from db.data.manager import load_fasttext_bin


class WordToWord:
    def __init__(self, threshold: float = 0.7, pretrained_model=None):
        """
        данный класс реализует функционал для выделения смысловых кластеров, ориентируясь на векторные представления
        слов некоторой предобученной модели.
        :param threshold: порог косинусной меры, который приемлим для того, чтобы считать вектора двух слов или
        вектор слова и множество векторов похожими друг на друга
        :param pretrained_model: предобученная модель, которая может извлекать веткора слов и реализует
        интерфейс gensim-а
        """
        self.__threshold = threshold
        if not pretrained_model:
            self.__model = load_fasttext_bin('fasttext_model/araneum_none_fasttextcbow_300_5_2018.model')
        else:
            self.__model = pretrained_model

    def set_threshold(self, new_threshold):
        if new_threshold > 1 or new_threshold < 0.0001:
            raise ValueError('Схожесть должна быть в интервале (0,1)')
        self.__threshold = new_threshold

    def __is_similar(self, target_word, other_words: List[str]) -> bool:
        target_word_vector = np.array([self.__model[target_word]])
        other_words_vectors = np.array([self.__model[word] for word in other_words])

        similarities = cosine_similarity(target_word_vector, other_words_vectors)[0]
        return np.mean(similarities) >= self.__threshold

    def extract_clusters(self, source_words: List[str]) -> List[List[str]]:
        """
        :param source_words: исходный набор уникальных слов
        :return: возвращает список кластеров. кластер - такое подмножесто слов, что у них общий смсысл
        """
        pairs = [list(tuple_) for tuple_ in combinations(source_words, 2)]

        word_groups = [pair for pair in pairs if self.__is_similar(pair[0], [pair[1]])]

        if not word_groups:
            return [source_words]

        return [self.__gain_cluster(group, source_words) for group in word_groups]

    def __gain_cluster(self, group: List[str], source_words: List[str]) -> List[str]:
        not_yet_included = list(set(source_words) - set(group))
        while not_yet_included:
            peek = not_yet_included.pop()
            if self.__is_similar(peek, group):
                group.append(peek)
        return group


if __name__ == '__main__':
    m = WordToWord()
    print('model is launched')
    s = None

    unique = ['труд', 'работа', 'творение']

    word_groups = m.extract_clusters(unique)
    for group in word_groups:
        print(group)
        print('-----')
    print('максимальный по длине:')
    ordered = sorted(word_groups, key=lambda x: len(x), reverse=True)
    print(ordered[0])
