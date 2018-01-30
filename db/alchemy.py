from sqlalchemy import create_engine, or_, and_, desc
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict
import datetime

from db.base import Base, Word, User, Synonym, Edition, Synset


class Alchemy:
    def __init__(self, path=''):
        engine = create_engine('sqlite:///{}'.format(path))
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.__session = DBSession()

    def get_session(self):
        return self.__session


