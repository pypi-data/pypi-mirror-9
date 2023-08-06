import json
from sqlalchemy import Column, Integer, String, Text

from plutonium.modules.orm.base import Base
from plutonium.modules.orm.types import JSONEncoded

class Output(Base):
    __tablename__ = 'outputs'

    id = Column(Integer, primary_key = True)
    name = Column(String(length=32), nullable = False)
    type = Column(String(length=32), nullable = False)
    params = Column(JSONEncoded)

    def get_handler(self):
        if self.type not in self.output_plugins:
            self.__logger__.warning("Unknown output type '%s'" % self.type)
            return None

        handler = self.output_plugins[self.type]

        return handler
