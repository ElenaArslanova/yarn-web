from typing import List

import numpy as np

from db.data.manager import load_word2vec_bin


class Word2VecOrdering:
    loaded_model = None

    @staticmethod
    def order_words_sequence_using_average_sim(words: List[str]) -> List[str]:
        """
        Приимает последовательность слов и возвращает упорядоченную последовательность этих же слов в соответствии с
        с их средней похожестью друг на друга, в порядке от самого похожего к наименнее похожему.
        То есть первое слово последовательности такое, на которое в среднем все остальные похожи больше, чем на
        следующее в этой же поседовательности
        :param words: массив слов
        :return: массив слов, упорядоченный в соответствии со схемой
        """
        words = np.array(words)

        if not Word2VecOrdering.loaded_model:
            Word2VecOrdering.set_up()
        matrix = np.array([[Word2VecOrdering.loaded_model.similarity(x, y)
                            if x in Word2VecOrdering.loaded_model and y in Word2VecOrdering.loaded_model and x != y else 0
                            for y in words]
                           for x in words])

        mean_scores = matrix.mean(axis=1)
        sorted_indexes = np.flip(np.argsort(mean_scores), axis=0)
        return list(words[sorted_indexes])

    @staticmethod
    def set_up(new_model_path: str = None):
        """
        инициализурет статический класс и, статическую переменную loaded_model некоторой предобученной моделью,
        которая лежит в каталоге db/data или же инициализирует модель по умолчанию
        :param new_model_path: имя модели
        :return: None
        """
        if new_model_path:
            Word2VecOrdering.loaded_model = load_word2vec_bin(new_model_path)
        else:
            Word2VecOrdering.loaded_model = load_word2vec_bin(
                'fasttext_model/araneum_none_fasttextcbow_300_5_2018.model')


if __name__ == '__main__':
    Word2VecOrdering.set_up()
    print(Word2VecOrdering.order_words_sequence_using_average_sim(['машина', 'стул', 'автомобиль', 'компьютер',
                                                                   'кабриолет']))
    # печатает ['машина', 'автомобиль', 'кабриолет', 'компьютер', 'стул']
