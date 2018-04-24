import random
from typing import Tuple, List, Dict
from collections import namedtuple

WordQuality = namedtuple('WordQuality', ['word', 'status'])


def results_as_dict(indexes: List[int], answers: List[Tuple[List, List]]) -> List[Dict]:
    """
    преобразует работу алгоритма в удобный для обработки вид: список из словарей
    каждый словарь описывается тремя строковыми ключами: id синсета,  list filtered и лист dropped
    :param indexes: id синсетов
    :param answers: результат работы алгоритма модели из base.py
    :return: лист из словарей
    """
    result_list = []
    for id, answer in zip(indexes, answers):
        clean, dirty = answer
        res = []
        res.extend([WordQuality(w, 'correct') for w in clean])
        res.extend(WordQuality(w, 'incorrect') for w in dirty)
        random.shuffle(res)
        result_list.append({'id': id, 'answer': res})
    return result_list
