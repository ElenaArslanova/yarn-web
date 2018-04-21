import math
from typing import List, Optional

import numpy as np
from gensim.models import FastText
from sklearn.metrics.pairwise import cosine_similarity

from models.layer_model import Definition


class FastTextWrapper:
    """
    Класс для оценки схожести определений по косинусной мере на основе их векторных представлений
    """

    def __init__(self, model_path: str, cosine_degree_angle_threshold=55):
        """
        :param model_path: путь до предъобученной бинарной модели
        :param cosine_degree_angle_threshold: пороговое значение для сравнения. Если угол не будет превосходить
        указанного знпчения при сравнении двух определений, то считается, что определения похожи
        """
        self.__threshold = cosine_degree_angle_threshold
        self.__model = FastText.load(model_path)

    def is_similar(self, target_definition: Definition, comparing_definitions: List[Definition]) -> bool:
        """
        сравнивает target_definition с каждым из comparing_definitions и если находится хоть одно определение для
        которого значение косинусной меры не превосходит  cosine_degree_angle_threshold, то возвращается True,
        Иначе - False
        :param target_definition: целевое определение
        :param comparing_definitions: список определений
        :return: bool
        """
        angles_as_degree = self.__get_cosine_similarity(target_definition, comparing_definitions)
        return min(angles_as_degree) <= self.__threshold

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
        angles_as_degree = self.__get_cosine_similarity(target_definition, comparing_definitions)
        min_angle = min(angles_as_degree)
        if use_threshold:
            if min_angle > self.__threshold:
                return None
            return comparing_definitions[angles_as_degree.index(min_angle)]
        return comparing_definitions[angles_as_degree.index(min_angle)]

    def __get_cosine_similarity(self, target_definition: Definition, comparing_definitions: List[Definition]) -> np.array:
        target_definition_vector = np.array([self.__model[target_definition.definition]])
        comparing_definitions_vectors = np.array([self.__model[x.definition] for x in comparing_definitions])
        cos_angles = cosine_similarity(target_definition_vector, comparing_definitions_vectors)[0]
        return [math.degrees(math.acos(x)) for x in cos_angles]



if __name__ == '__main__':
    m = FastTextWrapper('fasttext_model/araneum_none_fasttextcbow_300_5_2018.model')

    car_definitions = [
        Definition('машина','механизм, сложное сооружение, устройство для выполнения технологических операций, '
        'связанных с преобразованием, видоизменением энергии, материалов или информации'),
        Definition('машина', 'то же, что автомобиль'),
        Definition('машина', 'то же, что ускоритель'),
        Definition('машина', 'то же, что компьютер'),
        Definition('машина', 'государственная система, бюрократическая система')]

    automobile_definition = Definition('автомобиль', 'самоходное автономное безрельсовое колёсное транспортное средство ' \
                            'с приводом от бензинового, дизельного или электрического двигателя; машина')

    print(m.is_similar(automobile_definition, car_definitions))

    print(m.get_closest_def(automobile_definition, car_definitions))