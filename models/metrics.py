from typing import List

from models.processing import simple_normalization_tokens


def jacard_metric(w1, w2, d1: List[str], d2: List[str]) -> float:
    """
    метрика для тестов
    :param w1: слово, которому соответствует определение d1
    :param w2: лово, которому соответствует определение d2
    :param d1: определение первого слова в виде листа из слов
    :param d2: определение второго слова в виде листа из слов
    :return: схожесть d1 и d2 на основании коэффициента жакарра
    """
    d1 = set(d1)
    d2 = set(d2)

    return len(d1.intersection(d2)) / len((d1.union(d2)))


def jacard_with_word_influence(w1, w2, d1: List[str], d2: List[str]) -> float:
    """
    та же метрика жакарра, только если слово w1 встретилось в d2 или w2 в d1, то предполагается,
    что w1 и w2 точно синонимы
    :param w1: слово, которому соответствует определение d1
    :param w2: лово, которому соответствует определение d2
    :param d1: определение первого слова в виде листа из слов
    :param d2: определение второго слова в виде листа из слов
    :return: схожесть d1 и d2 на основании коэффициента жакарра + уточнение
    """
    if (w1 in d2) or (w2 in d1):
        return 1
    return jacard_metric(w1, w2, d1, d2)


def general_metric(w1: str, w2: str, d1: str, d2: str, sim_metric=jacard_metric,
                   processing=simple_normalization_tokens):
    """
    функция, которая должна использоваться везде при работе с метриками, обобщает поведение сравнения
    :param w1: слово, которому соответствует определение d1
    :param w2: слово, которому соответствует определение d2
    :param d1: определение первого слова
    :param d2: определение второго слова
    :param sim_metric: метрика схожести двух определений слов
    :param processing: нужно ли производить какую-либо обработку над строкой определения, по умолчанию проводится с
    помощью pymorphy, функция
    :return:
    """
    d1, d2 = processing(d1), processing(d2)
    return sim_metric(w1, w2, d1, d2)
