
import os
import re
import sys
import importlib
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

from plutonium.modules.tools import ucfirst

class Manager(object):

    def __init__(self, config):
        self.config = config
        self.factory = None

        self.__engine = None
        self.__sessions = []

    def __create_engine(self, echo = False):
        db_uri = self.config['database']['url'].value

        return sqlalchemy.create_engine(db_uri, echo = echo)

    def is_connected(self):
        if self.__engine is None:
            return False

        try:
            self.__engine.execute("SELECT 1")
        except:
            return False

        return True

    def get_engine(self):
        if not self.is_connected():
            self.__engine = self.__create_engine()

        return self.__engine

    def close_sessions(self):
        for sess in self.__sessions:
            sess.close()
        self.__sessions = []

    def create_session(self):
        session_factory = sessionmaker(bind=self.get_engine())
        session_class = scoped_session(session_factory)

        session = session_class()

        self.__sessions.append(session)

        return session
