import tqdm

from db.data.manager import load_alchemy
from db.base import SynsetWord, Word

def process_stripped_synset_words():
    session = load_alchemy('data.db').get_session()
    for s_word in tqdm.tqdm(session.query(SynsetWord).all()):
        found_word = False
        stripped = s_word.word.strip()
        if stripped != s_word.word:
            found_word = True
            corresponding_dict_word = session.query(Word).filter(Word.word == stripped).one_or_none()
            if corresponding_dict_word:
                s_word.word_id = corresponding_dict_word.id
            s_word.word = stripped
        if found_word:
            session.commit()


if __name__ == '__main__':
    process_stripped_synset_words()
