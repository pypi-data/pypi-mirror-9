
from sqlalchemy import Column, Integer, String, Enum

from plutonium.modules.orm.base import Base

class Filter(Base):
    __tablename__ = 'filters'

    id = Column(Integer, primary_key = True)
    name = Column(String(length=32), nullable = False)
    pattern = Column(String(length=64), nullable = False)
    source_node = Column(String(length=64), default = 'title')
    type = Column(Enum('black', 'white'), default = 'white')
