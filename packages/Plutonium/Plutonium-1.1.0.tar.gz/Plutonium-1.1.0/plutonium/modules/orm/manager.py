
import os
import re
import sys
import importlib
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from threading import Lock

from plutonium.modules.tools import ucfirst

class Manager(object):

    def __init__(self, config):
        self.config = config
        self.factory = None

        self.__engine = None
        self.__sessions = []

        """
            If SQLlite is used as database need to switch of the check_same_thread, because of design reason.
            But the SQLite is not thread safe so need to solve the safe resource sharing by manually,
            so the whole database connection handled as one shared resource.
        """
        self.lock = Lock()

    def __create_engine(self, echo = False):
        db_uri = self.config['database']['url'].value

        kwargs = dict(
            echo = echo,
            poolclass = StaticPool,
            connect_args = self.config['database']['connect_args'].sub_values()
        )

        return sqlalchemy.create_engine(db_uri, **kwargs)

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
