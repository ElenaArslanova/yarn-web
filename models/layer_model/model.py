import numpy as np
from typing import List, Dict, Iterable, Optional, Tuple
from functools import partial
from itertools import zip_longest
from collections import namedtuple, defaultdict
from pymorphy2 import MorphAnalyzer

from db.data.manager import load_alchemy
from models.base import Model
from models.metrics import general_metric, jacard_metric
from models.processing import remove_stop_words_tokens
from models.layer_model.base import Definition
from models.vector_embeddings import FastTextWrapper


# morph = MorphAnalyzer()

NewSynset = namedtuple('NewSynset', 'words definitions')


class Layer:
    #TODO: в новый синсет добавлять неизмененное слово, если оно как-то обрабатывалось (словосочетание)
    def __init__(self, word: str,
                 definitions: Optional[List[Definition]] = None):
        """
        :param word: слово синсета
        :param definitions: определения этого слова
        """
        self.word = word
        # self.original_word = word
        self.definitions = definitions if definitions else []
        self.next_layer = None

    # def _normalize_word(self):
    #     """
    #     если word - словосочетание, то выделяет в нем существительное и возвращает его
    #     :param word: слово из синсета
    #     :return:
    #     """
    #     parts = self.original_word.split()
    #     if len(parts) > 1:
    #         for part in parts:
    #             parsed = morph.parse(part)[0]
    #             if 'NOUN' in parsed.tag:
    #                 self.word = parsed.normal_form

    def all_definitions_are_linked(self) -> bool:
        for d in self.definitions:
            if not d.is_linked:
                return False
        return True

    def get_first_free_definition(self) -> Definition:
        for d in self.definitions:
            if not d.is_linked:
                d.is_linked = True
                return d

    def free_definitions_generator(self) -> Iterable[Definition]:
        for d in self.definitions:
            if not d.is_linked:
                yield d

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.word == other.word

    def __hash__(self):
        return hash(self.word)

    def __str__(self):
        return '{}:\n{}'.format(self.word, '\n'.join(str(d) for d in self.definitions))

    def __repr__(self):
        return 'Layer: {}'.format(self.word)


class LayerModel(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fasttext = FastTextWrapper()

    def set_fasttext_definition_strategy(self, new_strategy):
        self._fasttext.set_new_strategy(new_strategy)

    def set_fasttext_threshold(self, new_threshold):
        self._fasttext.set_new_threshold(new_threshold)

    def definitions_similarity(self, first: str, second: str) -> float:
        return self._metric(w1='', d1=first, w2='', d2=second)


    def _is_definition_in_chain(self, definition: Definition, chain: List[Definition]) -> bool:
        """
        :param definition: рассматриваемое определение
        :param chain: уже объединенные определения
        :return: можно ли включить определение в цепочку уже объединенных по смыслу определений из chain,
        т.е похоже ли оно на них по смыслу
        """
        return self._fasttext.is_similar(definition, chain)

    def _combine_similar_definitions(self, word: str, definitions: List[str]) -> List[Definition]:
        """
        Оставляет только уникальные по смыслу определения слова
        (например, если два определения похожи, то берется первое)
        :param definitions: список исходных определений
        :return: список разных по смыслу определений
        """
        # TODO: сделать объединение через fasttext
        similarity_matrix = self._create_similarity_matrix(definitions, self.definitions_similarity)
        similar_indices = self._matrix_processing(similarity_matrix)
        unique_meanings = [Definition(word, d) for d in
                           (definitions[i] for i in np.setdiff1d(np.arange(len(definitions)), similar_indices))]
        if similar_indices.any():
            combined_definition = Definition(word, definitions[similar_indices[0]])
            combined_definition.add_alternative_definitions(definitions[i] for i in similar_indices[1:])
            unique_meanings.append(combined_definition)
        return unique_meanings

    def _create_definitions(self, word: str, definitions: List[str]) -> List[Definition]:
        """
        создает список определений, считается, что каждое строковое определение из словаря уникально по смыслу
        :param definitions: список исходных определений
        :return:
        """
        return [Definition(word, d) for d in definitions]

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
                layers.append(Layer(word, self._create_definitions(word, definitions)))
        for adjacent in zip_longest(layers, layers[1:]):
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
        for d in next_layer.free_definitions_generator():
            if self._is_definition_in_chain(d, linked_definition):
                d.is_linked = True
                return d
        return None

    def _extract_new_synset_from_layers(self, layers: List[Layer]) -> NewSynset:
        """
        :param layers: уровни определений, созданные по синсетам
        :return: похожие по смыслу "слова" из разных уровней
        """
        definition_chain = []
        for layer in layers:
            if not layer.all_definitions_are_linked():
                if definition_chain:
                    next_definition = self._get_next_definition_to_link(definition_chain, layer)
                    if next_definition:
                        definition_chain.append(next_definition)
                else:
                    definition_chain.append(layer.get_first_free_definition())
        return NewSynset([d.word for d in definition_chain], definition_chain)

    def _filter_layers_with_no_definitions(self, layers: List[Layer]) -> Tuple[List[Layer], List[Layer]]:
        """
        разделяет уровни, у которых есть определения, от тех, у которых их нет
        :param layers: список уровней
        :return: список уровней с определениями и список уровней без определений
        """
        with_definitions, without_definitions = [], []
        for layer in layers:
            if layer.definitions:
                with_definitions.append(layer)
            else:
                without_definitions.append(layer)
        return with_definitions, without_definitions

    def _process_layers_without_definitions(self, new_synsets: List[NewSynset], layers: List[Layer]):
        """
        Пытается добавить слово из уровня без определений в какой-нибудь новый синсет, если оно похоже на слова из него.
        Слова, которые ни к какому синсету не подошли, добавляются в отдельный синсет
        :param new_synsets: созданные синсеты
        :param layers: уровни без определений
        :return:
        """
        unused_layers = set(layers)
        add_to_synset = defaultdict(list)  # непосредственно слова добавляются в синсет в самом конце,
                                           # чтобы оценка схожести считалась всегда по исходному синсету и не зависела
                                           # от порядка рассмотрения уровней из layers
        for i, synset in enumerate(new_synsets):
            for layer in layers:
                if self._fasttext.is_word_similar_to_list(layer.word, synset.words):
                    add_to_synset[i].append(layer)
                    if layer in unused_layers:
                        unused_layers.remove(layer)
        for i in add_to_synset:
            new_synsets[i].words.extend(layer.word for layer in add_to_synset[i])
        if unused_layers:
            new_synsets.append(NewSynset([l.word for l in unused_layers], None))

    def extract_new_synsets(self, synset_definition: Dict[str, List[str]]) -> List[NewSynset]:
        """
        выделяет из данного синсета новые по смыслу слов, слова без определений в словаре собираются в отдельный синсет
        :param synset_definition: слова синсета с определениями (из базы)
        :return: список новых выделенных по смыслу синсетов
        """
        layers = self._create_layers(synset_definition)
        layers_with_definitions, layers_without_definitions = self._filter_layers_with_no_definitions(layers)
        synsets = []
        while True:
            new_synset = self._extract_new_synset_from_layers(layers_with_definitions)
            if not new_synset.words:
                break
            synsets.append(new_synset)
        if layers_without_definitions:
            print(layers_without_definitions)
            self._process_layers_without_definitions(synsets, layers_without_definitions)
        return synsets

    def _matrix_processing(self, matrix):
        rows, _ = np.where(matrix >= self._threshold)
        return np.unique(rows)


if __name__ == '__main__':
    metric = partial(general_metric, sim_metric=jacard_metric, processing=remove_stop_words_tokens)
    model = LayerModel(0.00001, metric)
    alchemy = load_alchemy('data.db')

    yarn_ids, synset_definitions = alchemy.get_synsets_definitions((508, 508))
    for p in synset_definitions:
        print(list(p.keys()))
    print()
    for s in model.extract_new_synsets(synset_definitions[0]):
        print('Новый синсет: {}'.format(', '.join(s.words)))
        if s.definitions:
            print('Определения:')
            for d in s.definitions:
                print('\t{}'.format(d))
        else:
            print('Нет определений в словаре')
        print('-------------------')

    # print('-------------CLOSEST STRATEGY-----------------')
    # model.set_fasttext_definition_strategy('closest')
    # for s in model.extract_new_synsets(synset_definitions[0]):
    #     print('Новый синсет: {}'.format(', '.join(s.words)))
    #     if s.definitions:
    #         print('Определения:')
    #         for d in s.definitions:
    #             print('\t{}'.format(d))
    #     else:
    #         print('Нет определений в словаре')
    #     print('-------------------')
