import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from models.layer_model.model import NewSynset


class Cluster:
    """
    хранит множество синсетов, похожих по смыслу
    в момент применения ко всем данным ярна  нужен для быстрого слияния (и проверки того, можно ли слить)
    """

    def __init__(self, initial_synset: NewSynset, initial_synset_vector: np.ndarray):
        """
        :param initial_synset: синсет, который порождает кластер
        :param fasttext_model: модель, на основе которой будет производиться сравнене
        :param threshold
        """
        self.__synsets = [initial_synset]
        self.__vectors = [initial_synset_vector]

    def similarity_to(self, synset: NewSynset, synset_vector: np.ndarray) -> float:
        """
        Возвращает схожесть синсета на кластер
        :param synset: синсет
        :param synset_vector: вектор синсета
        :return: косинусную близость
        """
        return np.mean(cosine_similarity([synset_vector], self.__vectors)[0])

    def add(self, synset: NewSynset, synset_vector: np.ndarray):
        """
        Добавлят синсет и его вектор в кластер
        :param synset: синсет
        :param synset_vector: вектор синсета
        :return: None
        """
        self.__synsets.append(synset)
        self.__vectors.append(synset_vector)

    def size(self):
        """
        возвращает размер кластера
        :return: int
        """
        return len(self.__synsets)

    def print_cluster(self):
        print('------------------')
        for w in self.__synsets:
            print(w.words)
        print('------------------')

    def __str__(self):
        synsets_as_string = [';'.join(x.words) for x in self.__synsets]
        return ';'.join(synsets_as_string)


if __name__ == '__main__':
    pass
