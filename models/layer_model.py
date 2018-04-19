import numpy as np
from typing import List, Dict, Iterable, Optional
from functools import partial
from itertools import combinations

from models.base import Model
from models.metrics import general_metric, jacard_metric
from models.processing import remove_stop_words_tokens

from db.alchemy import Alchemy


class Definition:
    def __init__(self, definition: str):
        self.definition = definition
        self.alternatives = []
        self.linked_definition = None

    def add_alternative_definition(self, alternative: str):
        self.alternatives.append(alternative)

    def add_alternative_definitions(self, alternatives: Iterable[str]):
        self.alternatives.extend(alternatives)

    def link(self, definition_to_link):
        self.linked_definition = definition_to_link

    def is_linked(self):
        return bool(self.linked_definition)

    def __str__(self):
        return 'Definition: {}, alternatives: {}'.format(self.definition, self.alternatives)

    def __repr__(self):
        return str(self)


class Layer:
    def __init__(self, word: str,
                 definitions: Optional[List[Definition]] = None):
        """
        :param word: слово синсета
        :param definitions: определения этого слова
        """
        self.word = word
        self.definitions = definitions if definitions else []
        # self.adjacent_layers = []
        self.next_layer = None

    # def add_adjacent_layer(self, adjacent):
    #     self.adjacent_layers.append(adjacent)
    #
    # def add_adjacent_layers(self, layers):
    #     self.adjacent_layers.extend(layers)

    def all_definitions_are_linked(self) -> bool:
        for d in self.definitions:
            if not d.is_linked():
                return False
        return True

    def get_free_definition(self) -> Iterable[Definition]:
        for d in self.definitions:
            if not d.is_linked():
                yield d

    def __str__(self):
        return '{}:\n{}'.format(self.word, '\n'.join(str(d) for d in self.definitions))

    def __repr__(self):
        return 'Layer: {}'.format(self.word)



class LayerModule(Model):
    def definitions_similarity(self, first: str, second: str) -> float:
        return self._metric(w1='', d1=first, w2='', d2=second)

    def _is_definition_in_chain(self, definition: Definition, chain: List[Definition],
                               threshold=None) -> bool:
        """
        :param definition: рассматриваемое определение
        :param chain: уже объединенные определения
        :param threshold: порог при сравнение определений по какой-либо метрике
        :return: можно ли включить определение в цепочку уже объединенных по смыслу определений из chain,
        т.е похоже ли оно на них по смыслу
        """
        #TODO: научиться сравнивать определение с несколькими, пока сравнивается текст текущего с текстом самого последнего добавленного
        return self.definitions_similarity(definition.definition, chain[-1].definition) > 0.6

    def _combine_similar_definitions(self, definitions: List[str]) -> List[Definition]:
        """
        Оставляет только уникальные по смыслу определения слова
        (например, если два определения похожи, то берется первое)
        :param definitions: список исходных определений
        :return: список разных по смыслу определений
        """
        similarity_matrix = self._create_similarity_matrix(definitions, self.definitions_similarity)
        similar_indices = self._matrix_processing(similarity_matrix)
        unique_meanings = [Definition(d) for d in
                           (definitions[i] for i in np.setdiff1d(np.arange(len(definitions)), similar_indices))]
        if similar_indices.any():
            combined_definition = Definition(definitions[similar_indices[0]])
            combined_definition.add_alternative_definitions(definitions[i] for i in similar_indices[1:])
            unique_meanings.append(combined_definition)
        return unique_meanings

    def _create_layers(self, synset_definition: Dict[str, List[str]]) -> List[Layer]:
        """
        :param synset_definitions: слова синсета с определениями
        :return: уровни из уникальных определений слов
        """
        layers = []
        for word in synset_definition:
            definitions = synset_definition[word]
            if not definitions:
                layers.append(Layer(word))
            else:
                layers.append(Layer(word, self._combine_similar_definitions(definitions)))
        # adjacent_layers = combinations(layers, 2)
        # for adjacent in adjacent_layers:
        #     adjacent[0].add_adjacent_layer(adjacent[1])
        #     adjacent[1].add_adjacent_layer(adjacent[0])
        for adjacent in zip(layers, layers[1:]):
            adjacent[0].next_layer = adjacent[1]
        return layers

    def _get_next_definition_to_link(self, linked_definition: List[Definition],
                                    next_layer: Layer) -> Optional[Definition]:
        """
        :param linked_definition: определения, объединенные на предыдущих шагах
        :param next_layer: следующий уровень
        :return: определение на следующем уровне, если такое есть, похожее по смыслу на уже объединенные
        """
        if next_layer.all_definitions_are_linked():
            return None
        for d in next_layer.get_free_definition():
            if self._is_definition_in_chain(d, linked_definition):
                return d
        return None

    def get_definition_chain_from_layers(self, layers: List[Layer]) -> List[Definition]:
        """
        :param layers: уровни определений, созданные по синсетам
        :return: похожие по смыслу определения из разных уровней
        """
        # TODO: implement
        pass


    def filter_synset(self, synset_definition: Dict[str, List[str]]):
        layers = self._create_layers(synset_definition)
        definition_chains = []
        cur_chain = []
        visited_layers = set()
        # TODO: переписать c использованием get_definition_chain_from_layers
        while stack:
            layer = stack.pop()
            for adjacent in layer.adjacent_layers:
                if adjacent.word not in visited_layers and not adjacent.all_definitions_are_linked():
                    next_definition_in_chain = self._get_next_definition_to_link(cur_chain, adjacent)
                    if next_definition_in_chain:
                        cur_chain.append(next_definition_in_chain)
                        stack.append(adjacent)
                        break
            visited_layers.add(layer.word)


    def _matrix_processing(self, matrix):
        rows, _ = np.where(matrix >= self._threshold)
        return np.unique(rows)


if __name__ == '__main__':
    metric = partial(general_metric, sim_metric=jacard_metric, processing=remove_stop_words_tokens)
    model = LayerModule(0.00001, metric)
    alchemy = Alchemy(path='../db/data.db')
    yarn_ids, synset_definitions = alchemy.get_synsets_definitions((505, 507))
    for p in synset_definitions:
        print(p)
    model.filter_synset(synset_definitions[0])
