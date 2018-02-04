from string import punctuation
from typing import List, Callable, Optional

from pymorphy2.tokenizers import simple_word_tokenize
from pymorphy2 import analyzer

morph = analyzer.MorphAnalyzer()

with open('stopwords.txt') as f:
    stopwords = set(f.read().split())


def tokenize(definition: str) -> List[str]:
    """
    разбивает строку на токены
    :param definition: строка - определение
    :return: токены (без знаков препинания)
    """
    return [x for x in simple_word_tokenize(definition) if x not in punctuation]


def simple_normalization_tokens(definition: str) -> List[str]:
    """
    разбивает на токены входное предложение, нормализует их и возвращает лист слов в инфинитиве
    :definition: строка - определение
    :return:
    """
    return [morph.parse(x)[0].normal_form for x in tokenize(definition)]


def remove_stop_words_tokens(definition: str,
                             normalize: Optional[Callable[[str], List[str]]]=simple_normalization_tokens) -> List[str]:
    """
    убирает из предложения стоп-слова
    :param definition: строка - определение
    :param normalize: функция для предварительной нормализации слов
    :return: отфильтрованный список слов
    """
    tokens = normalize(definition) if normalize else tokenize(definition)
    return [x for x in tokens if x not in stopwords]
