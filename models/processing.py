from string import punctuation
from typing import List

from pymorphy2.tokenizers import simple_word_tokenize
from pymorphy2 import analyzer

morph = analyzer.MorphAnalyzer()


def simple_normalization_tokens(definition: str) -> List[str]:
    """
    разбивает на токены входное предложение, нормализует их и возвращает лист слов в инфинитиве
    :definition: строка - определение
    :return:
    """
    return [morph.parse(x)[0].normal_form for x in simple_word_tokenize(definition) if x not in punctuation]
