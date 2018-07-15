import random
from typing import List

import pandas as pd
import numpy as np

from apply.cluster import Cluster
from db.data.manager import load_alchemy, load_fasttext_bin
from models.layer_model.additional import Word2VecOrdering
from models.layer_model.model import LayerModel, NewSynset


class DefDict:
    def __init__(self):
        self.__dictionary = {}
        self.__alchemy = load_alchemy('data.db')

    def get_synset_definitions(self, synset: List[str]):
        """
        Возвращает словарь определений для синсета
        :param synset: лист слов
        :return: словарь вида dict[word] = List[str] - список определений
        """
        need_description = [w for w in synset if w not in self.__dictionary]
        new_words_with_descriptions = self.__alchemy.get_words_definitions(need_description)

        for new_word in new_words_with_descriptions:
            self.__dictionary[new_word] = new_words_with_descriptions[new_word]

        return {x: self.__dictionary[x] for x in synset}


class ClustersHolder:
    def __init__(self, threshold=0.4):
        self.__clusters = []
        self.__fasttext = load_fasttext_bin('fasttext_model/araneum_none_fasttextcbow_300_5_2018.model')
        self.__threshold = threshold

    def process_synsets(self, synsets: List[NewSynset]):
        """
        обрабатывает список синсетов, доабавляя каждый в существующий кластер, либо в новый
        :param synsets: список синсетов
        :return: None
        """
        where_to_add = {}
        for synset in synsets:
            synset_vector = self.__extract_vector(synset)
            if type(synset_vector) != np.ndarray:
                print('Проблемный синсет - не удалось извлечь вектор, далее такой синсет не будет учитываться')
                continue

            if self.__clusters:
                similarities = [c.similarity_to(synset, synset_vector) for c in self.__clusters]
                max_similarity_idx = np.argmax(similarities)
                # если синсет похож на какой-то кластер, то данный синсет будет в него добавлен
                # иначе синсет породит новый кластер
                if similarities[max_similarity_idx] >= self.__threshold:
                    where_to_add[synset] = (max_similarity_idx, synset_vector)
                else:
                    where_to_add[synset] = (-1, synset_vector)
            else:
                where_to_add[synset] = (-1, synset_vector)

        for synset in where_to_add:
            idx, vector = where_to_add[synset]
            if idx == -1:
                self.__clusters.append(Cluster(synset, vector))
            else:
                self.__clusters[idx].add(synset, vector)

    def save_clusters_to_frame(self, name=''):
        words = []
        vectors = []
        pass

    def __extract_vector(self, synset: NewSynset):
        if synset.definitions:
            try:
                return self.__fasttext[synset.definitions[random.randint(0, len(synset.definitions - 1))]]
            except KeyError:
                try:
                    return self.__fasttext[synset.words[random.randint(0, len(synset.words) - 1)]]
                except KeyError:
                    return None
        else:
            try:
                return self.__fasttext[synset.words[random.randint(0, len(synset.words) - 1)]]
            except KeyError:
                return None


if __name__ == '__main__':
    model = LayerModel(0.45, None)
    model.set_fasttext_definition_strategy('average')

    read_count = 0  # сколько всего прочитано строк
    d = DefDict()  # словарь
    ch = ClustersHolder()  # лежат все кластеры

    chunk_size = 100  # сколько синсевто будет считано в одну тиреацию
    from_start = True
    # TODO нужно учесть, что мы сохраняем данные и если что-то упадет, то заново все считывать не надо

    # после каждой итерации будет производиться сохранение результата, чтобы если что-то упало, это можно было бы не
    # перечитывать
    while read_count < 70468:  # столько синсетов всего
        sub_frame = pd.read_csv('yarn-synsets.csv', skiprows=read_count, chunksize=chunk_size)
        for _, row in sub_frame.iterrows():
            words = row.words.split(';')
            ordered_words = Word2VecOrdering.order_words_sequence_using_average_sim(words)

            model_input = d.get_synset_definitions(ordered_words)  # словарь вида word: List[str] - список определений
            model_output = model.extract_new_synsets(model_input)
            ch.process_synsets(model_output)

        print('Прочитано строк в итерации: {}'.format(sub_frame.shape[0]))
        print('Сохранение промежуточного результата в фрейм')
        last_pointer = read_count
        read_count += sub_frame.shape[0]
        ch.save_clusters_to_frame('clusters{}_{}.csv'.format(last_pointer, read_count))
        print('Сохранен результат текущей итерации в файл {}'.format('clusters{}_{}.csv'.format(last_pointer, read_count)))


