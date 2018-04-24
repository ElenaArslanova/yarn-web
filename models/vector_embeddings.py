import math
from typing import List, Optional

import numpy as np
from gensim.models import FastText
from sklearn.metrics.pairwise import cosine_similarity

from models.layer_model.base import Definition


class FastTextWrapper:
    """
    Класс для оценки схожести определений по косинусной мере на основе их векторных представлений
    """

    def __init__(self, model_path: str, cosine_sim_threshold=0.573):
        """
        :param model_path: путь до предъобученной бинарной модели
        :param cosine_sim_threshold: пороговое значение для сравнения. Если схожесть не будет превосходить
        указанного знпчения при сравнении двух определений, то считается, что определения похожи
        """
        self.__threshold = cosine_sim_threshold
        self.__model = FastText.load(model_path)

    def set_new_threshold(self, new_cosine_sim_threshold=0.573):
        if new_cosine_sim_threshold > 1 or new_cosine_sim_threshold < 0.0001:
            raise ValueError('Схожесть должна быть в интервале (0,1)')
        self.__threshold = new_cosine_sim_threshold

    def is_similar(self, target_definition: Definition, comparing_definitions: List[Definition]) -> bool:
        """
        сравнивает target_definition с каждым из comparing_definitions и если находится хоть одно определение для
        которого значение косинусной меры превосходит  cosine_degree_angle_threshold, то возвращается True,
        Иначе - False
        :param target_definition: целевое определение
        :param comparing_definitions: список определений
        :return: bool
        """
        sim = self.__get_cosine_similarity(target_definition, comparing_definitions)
        return max(sim) >= self.__threshold

    def get_closest_def(self, target_definition, comparing_definitions: List[Definition], use_threshold=True) -> \
            Optional[Definition]:
        """
        сравнивает target_definition с каждым из comparing_definitions и если находится хоть одно определение для
        которого значение косинусной меры не превосходит  cosine_degree_angle_threshold при условии, что стоит use_threshold,
        возвращает самое похожее, иначе - возвращает любое самое похожее
        :param target_definition: целевое определение
        :param comparing_definitions: список определений
        :return: Definition
        """
        cosine_similarities = self.__get_cosine_similarity(target_definition, comparing_definitions)
        max_sim_idx = np.argmax(cosine_similarities)
        max_sim = cosine_similarities[max_sim_idx]
        if use_threshold:
            if max_sim < self.__threshold:
                return None
            return comparing_definitions[max_sim_idx]
        return comparing_definitions[max_sim_idx]

    def __get_cosine_similarity(self, target_definition: Definition,
                                comparing_definitions: List[Definition]) -> np.array:
        target_definition_vector = np.array([self.__model[target_definition.definition]])
        comparing_definitions_vectors = np.array([self.__model[x.definition] for x in comparing_definitions])
        return cosine_similarity(target_definition_vector, comparing_definitions_vectors)[0]

        # TODO: метод, принимающий список слов и возвращающий матрицу схожести каждого с каждым, similarity(w, w)=0


if __name__ == '__main__':
    m = FastTextWrapper('layer_model/fasttext_model/araneum_none_fasttextcbow_300_5_2018.model')

    car_definitions = [
        Definition('машина', 'механизм, сложное сооружение, устройство для выполнения технологических операций, '
                             'связанных с преобразованием, видоизменением энергии, материалов или информации'),
        Definition('машина', 'то же, что автомобиль'),
        Definition('машина', 'то же, что ускоритель'),
        Definition('машина', 'то же, что компьютер'),
        Definition('машина', 'государственная система, бюрократическая система')]

    automobile_definition = Definition('автомобиль',
                                       'самоходное автономное безрельсовое колёсное транспортное средство ' \
                                       'с приводом от бензинового, дизельного или электрического двигателя; машина')

    print(m.is_similar(automobile_definition, car_definitions))

    print(m.get_closest_def(automobile_definition, car_definitions))
