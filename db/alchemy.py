from typing import Dict, List, Tuple

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from db.base import Base, Word, User, Synonym, Edition, Synset, SynsetWord, Definition, WordDefinitionRelation


class Alchemy:
    def __init__(self, path=''):
        engine = create_engine('sqlite:///{}'.format(path))
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.__session = DBSession()

    def get_session(self):
        return self.__session

    def get_synsets_definitions(self, synset_id_range: Tuple[int, int] = (1,)) -> Tuple[List[int],
                                                                                        List[Dict[str, List[str]]]]:
        """
        :param synset_id_range: диапазон id синсетов, которые нужно вернуть с их определениями
        :return: возвращает лист словарей,  где в каждом словаре:
        ключ - слово из синсета, значение - лист определений для данного слова из базы. Если слова нет в базе,
        то ему приписывается в виде определения None. Также возвращается лист идентификаторов yarn_id для каждого
        синсета
        """
        if len(synset_id_range) == 1:
            left, right = synset_id_range[0], synset_id_range[0]
        else:
            left, right = synset_id_range

        relations = self.__session.query(Synset, SynsetWord, WordDefinitionRelation) \
            .filter(and_(Synset.id >= left, Synset.id <= right)) \
            .filter(Synset.id == SynsetWord.synset_id) \
            .outerjoin(WordDefinitionRelation, WordDefinitionRelation.word_id == SynsetWord.word_id) \
            .all()
        if not relations:
            raise IndexError("synsets' ids are out of range")
        yarn_ids = sorted(set(x[0].yarn_id for x in relations))
        with_definition = set(relation[2].id for relation in relations if relation[2] is not None)
        definitions = {d.id: d.definition
                       for d in self.__session.query(Definition).filter(Definition.id.in_(with_definition)).all()} \
            if with_definition else {}

        syn_ids = set(relation[0].id for relation in relations)

        request = []
        for id in sorted(syn_ids):
            relations_filtered = [r for r in relations if r[0].id == id]
            syn = {}
            for r in relations_filtered:
                word = r[1].word
                if r[2]:
                    definition = definitions[r[2].id]
                    if word in syn:
                        syn[word].append(definition)
                    else:
                        syn[word] = [definition]
                else:
                    syn[word] = None
            request.append(syn)
        return yarn_ids, request

    def get_synset_definitions(self, synset_id: int):
        """
        частный случай запроса ко всем синсетам
        :param synset_id: id синсета из базы
        :return: словарь, в котором ключи - слова из синсета, значения - листы из определений для слов
        """
        return self.get_synsets_definitions((synset_id, synset_id))

    def get_word_definitions(self, word: str) -> List[str]:
        """
        принимает слово и возвращает все имеющиеся в базе определения
        :param word: слово
        :return: список определений слова
        """
        definitions = self.__session.query(Definition.definition).filter(Word.word == word) \
            .filter(Word.id == WordDefinitionRelation.word_id) \
            .filter(WordDefinitionRelation.definition_id == Definition.id).all()
        if not definitions:
            return []
        return [x[0] for x in definitions]

    def get_words_definitions(self, words: List[str]):
        result = {}
        for word in words:
            definitions = self.get_word_definitions(word)
            if not definitions:
                result[word] = None
            else:
                result[word] = definitions
        return result

    def get_concatenated_synsets_by_yarn_ids(self, yarnd_ids: List[int]):
        result = set()
        for idx in yarnd_ids:
            result.update(self.__session.query(Synset).filter(Synset.yarn_id == idx).one().synset.split(';'))
        return result


if __name__ == '__main__':
    a = Alchemy('data.db')
    print(len(a.get_concatenated_synsets_by_yarn_ids(yarnd_ids=[1,5])))