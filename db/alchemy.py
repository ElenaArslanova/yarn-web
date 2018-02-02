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

    def get_synsets_definitions(self, synset_id_range: Tuple[int, int] = (1,)) -> List[Dict[str, List[str]]]:
        """
        :param synset_id_range: диапозон id синсетов, которые нужно вернуть с их определениями
        :return: возвращает лист словарей,  где в каждом словаре:
        ключ - слово из синсета, значение - лист определений для данного слова из базы. Если слова нет в базе,
        то ему приписывается в виде определения None
        """
        if len(synset_id_range) == 1:
            left, right = synset_id_range[0], synset_id_range[0]
        else:
            left, right = synset_id_range

        synsets = self.__session.query(Synset, SynsetWord, Definition) \
            .filter(and_(Synset.id >= left, Synset.id <= right)) \
            .filter(Synset.id == SynsetWord.synset_id) \
            .filter(WordDefinitionRelation.word_id == SynsetWord.word_id) \
            .filter(Definition.id == WordDefinitionRelation.definition_id) \
            .all()
        if not synsets:
            return []

        ids = set(map(lambda x: x[0].id, synsets))

        request = []
        for id in ids:
            by_condition = list(filter(lambda x: x[0].id == id, synsets))
            synset_ = map(lambda x: (x[1].word, x[2].definition), by_condition)
            raw_syn = set(list(map(lambda x: x[0].synset, by_condition))[0].split(';'))
            syn = dict()
            for k, v in synset_:
                if k in syn:
                    syn[k].append(v)
                else:
                    syn[k] = [v]
            syn.update((x, None) for x in raw_syn - syn.keys())
            request.append(syn)

        return request

    def get_synset_definitions(self, synset_id: int):
        """
        частный случай запроса ко всем синсетам
        :param synset_id: id синсета из базы
        :return: словарь, в котором ключи - слова из синсета, значения - листы из определений для слов
        """
        return self.get_synsets_definitions((synset_id, synset_id))[0]


if __name__ == '__main__':
    # a = Alchemy()
    # print(a.get_synset_definitions(1))
    pass