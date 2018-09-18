from typing import List

import numpy as np

from apply.cluster import Cluster
from db.data.manager import load_alchemy, load_fasttext_bin
from models.layer_model.model import NewSynset


class DefDict:
    def __init__(self):
        self.__dictionary = {}
        self.__alchemy = load_alchemy('data.db')

    def get_synset_definitions(self, synset: List[str]):
        """
        Возвращает словарь определений для синсета
        :param synset: лист слов
        :return: словарь вида dict[word] = List[Definition] - список определений
        """
        need_description = [w for w in synset if w not in self.__dictionary]
        new_words_with_descriptions = self.__alchemy.get_words_definitions(need_description)

        for new_word in new_words_with_descriptions:
            self.__dictionary[new_word] = new_words_with_descriptions[new_word]
        definitions = {x: self.__dictionary[x] for x in synset}
        for word in definitions:
            if definitions[word]:
                for d in definitions[word]:
                    d.is_linked = None
        return definitions


class ClustersHolder:
    def __init__(self, threshold=0.4):
        self.__clusters = []
        self.problem_synsets = []
        self.__fasttext = load_fasttext_bin('fasttext_model/araneum_none_fasttextcbow_300_5_2018.model')
        self.__threshold = threshold

    def process_synsets(self, synsets: List[NewSynset]):
        """
        обрабатывает список синсетов, доабавляя каждый в существующий кластер, либо в новый
        :param synsets: список синсетов
        :return: None
        """
        where_to_add = {}
        for i, synset in enumerate(synsets):
            synset_vector = self.__extract_vector(synset)
            if type(synset_vector) != np.ndarray:
                print('Проблемный синсет - не удалось извлечь вектор, далее такой синсет не будет учитываться, '
                      'но он будет записан')
                print(synset.words)
                self.problem_synsets.append(synset.words)
                continue

            if self.__clusters:
                similarities = [c.similarity_to(synset, synset_vector) for c in self.__clusters]
                max_similarity_idx = np.argmax(similarities)
                # если синсет похож на какой-то кластер, то данный синсет будет в него добавлен
                # иначе синсет породит новый кластер
                if similarities[max_similarity_idx] >= self.__threshold:
                    where_to_add[i] = (max_similarity_idx, synset_vector)
                else:
                    where_to_add[i] = (-1, synset_vector)
            else:
                where_to_add[i] = (-1, synset_vector)

        for synset_number in where_to_add:
            synset = synsets[synset_number]
            idx, vector = where_to_add[synset_number]
            if idx == -1:
                self.__clusters.append(Cluster(synset, vector))
            else:
                self.__clusters[idx].add(synset, vector)

    def save_clusters_to_frame(self, name=''):
        words = []
        vectors = []
        pass

    def __extract_vector(self, synset: NewSynset):
        """
        логика извлечения следующая: если у синсета нет определений, то автоматически вернется None
        в противном случае будет попытка извлечь вектор хоть для какого-то определения и если ни для одного определения
        этого сделать не удалось - вернется None
        :param synset: новый синсет
        :return: вектор определения этого синсета
        """
        if not synset.definitions:
            return None

        for definition_object in synset.definitions:
            try:
                return self.__fasttext[definition_object.definition]
            except KeyError:
                continue
        return None

