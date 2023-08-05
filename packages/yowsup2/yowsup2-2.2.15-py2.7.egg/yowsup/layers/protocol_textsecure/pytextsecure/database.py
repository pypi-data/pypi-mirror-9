from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os.path import expanduser
import os
# yowdir = expanduser("~/.yowsup")
# db_name = "config.db"
# db_path = yowdir
# os.makedirs(yowdir)

# engine = create_engine('sqlite:////home/tarek/config.db', echo=False)
# session = scoped_session(sessionmaker(bind=engine))

#Base = declarative_base()
#Base.query = session.query_property()

#
# def init_db():
#     import dbmodel
#     Base.metadata.create_all(engine)

class TextSecureDatabase(object):

    __instance = None

    def __init__(self, path):
        self.engine = create_engine(path, echo=False)
        self.session = scoped_session(sessionmaker(bind = self.engine))
        TextSecureDatabase.__instance = self

    def init_db(self, base):
        base.query = self.session.query_property()
        base.metadata.create_all(self.engine)

    @staticmethod
    def get():
        if not TextSecureDatabase.__instance:
            raise ValueError("Database is not initialized")
        return TextSecureDatabase.__instance
