
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.declarative import declarative_base

import collections

class CustomBase(object):

    def __iter__(self):
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if type(attr) is not InstrumentedAttribute:
                continue
            yield (name, getattr(self, name))

    def __repr__(self):
        data = dict(self)
        return "<%s(%s)>" % (self.__class__.__name__, ', '.join(["%s=%s" % (name, data[name]) for name in data]))

    def __eq__(self, other):

        if other is None:
            return False

        if not isinstance(other, collections.Iterable):
            return False

        return dict(self) == dict(other)


Base = declarative_base(cls=CustomBase)
