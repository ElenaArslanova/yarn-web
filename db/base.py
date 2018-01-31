from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    email = Column(String)

    def __init__(self, login, email):
        self.login = login
        self.email = email


class Word(Base):
    __tablename__ = 'word'
    id = Column(Integer, primary_key=True)
    word = Column(String)
    pos = Column(String)

    def __init__(self, word, pos):
        self.word = word
        self.pos = pos


class Synonym(Base):
    __tablename__ = 'synonym'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('word.id'))
    synonym = Column(String)

    def __init__(self, word_id, synonym):
        self.word_id = word_id
        self.synonym = synonym


class Definition(Base):
    __tablename__ = 'definition'
    id = Column(Integer, primary_key=True)
    definition = Column(String)

    def __init__(self, definition):
        self.definition = definition


class WordDefinitionRelation(Base):
    __tablename__ = 'wordDefinitionRelation'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('word.id'))
    definition_id = Column(Integer, ForeignKey('definition.id'))

    def __init__(self, word_id, definition_id):
        self.word_id = word_id
        self.definition_id = definition_id


class Synset(Base):
    __tablename__ = 'synset'
    id = Column(Integer, primary_key=True)
    synset = Column(String)
    grammar = Column(String)
    domain = Column(String)
    yarn_id = Column(Integer)

    def __init__(self, synset, grammar, domain, yarn_id):
        '''
        :param synset: строка, представляющая synset
        '''
        self.synset = synset
        self.grammar = grammar
        self.domain = domain
        self.yarn_id = yarn_id


class SynsetWord(Base):
    __tablename__ = 'synsetWord'
    id = Column(Integer, primary_key=True)
    synset_id = Column(Integer, ForeignKey('synset.id'))
    word = Column(String)
    word_id = Column(Integer, ForeignKey('word.id'))

    def __init__(self, synset_id, word, word_id):
        self.synset_id = synset_id
        self.word = word
        self.word_id = word_id


class Edition(Base):
    __tablename__ = 'edition'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    synset_id = Column(String, ForeignKey('synset.id'))
    edited_synset = Column(String)
    datetime = Column(DateTime(timezone=True))

    def __init__(self, user_id, synset_id, edited_synset, datetime):
        '''
        :param user_id: id пользователя, внесшего изменение
        :param synset_id: id исходного synset'а
        :param edited_synset: новый synset в виде строки
        :param datetime: дата и время изменения
        '''
        self.user_id = user_id
        self.synset_id = synset_id
        self.edited_synset = edited_synset
        self.datetime = datetime


if __name__ == '__main__':
    engine = create_engine('sqlite:///data.db')
    Base.metadata.create_all(engine)
