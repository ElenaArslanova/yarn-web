import json
import tqdm

from db.alchemy import Alchemy
from db.base import Word, Definition, WordDefinitionRelation


alchemy = Alchemy(path='data.db')


def create_from_dictionary(path, session_add_bound):
    session = alchemy.get_session()
    session_counter = 0
    word_index = 1
    definition_index = 1
    word_id_buffer = set()
    relations_buffer = []
    with open(path) as f:
        for line in tqdm.tqdm(f):
            if session_counter == session_add_bound:
                session.commit()
                session.add_all([WordDefinitionRelation(w, d) for w, d in relations_buffer])
                relations_buffer.clear()
                session_counter = 0
            dict_entry = json.loads(line)
            if 'definition' in dict_entry:
                definitions = [Definition(d) for d in dict_entry['definition']]
                word_entry = dict_entry['word'][0]
                words = []
                if word_entry in word_id_buffer:
                    word_id_buffer.clear()
                    word_id_buffer.add(word_entry)
                else:
                    word = Word(word_entry, dict_entry['POS'])
                    words.append(word)
                for _ in definitions:
                    relations_buffer.append((word_index, definition_index))
                    definition_index += 1
                word_index += 1
                session.add_all(words)
                session.add_all(definitions)
                session_counter += 1
    session.commit()


if __name__ == '__main__':
    create_from_dictionary('dicts/ru.wikt_final.json', 100)
    # s = alchemy.get_session()
    # for q in s.query(Word).filter(Word.word == 'отпор').all():
    #     print(q.id, q.word)
    # for q in s.query(Definition).filter(Definition.id == 91180).all():
    #     print(q.id, q.definition)
    # for q in s.query(WordDefinitionRelation).filter(WordDefinitionRelation.word_id == 68570).all():
    #     print(q.id, q.word_id, q.definition_id)