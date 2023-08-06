
import json
import os
from abc import abstractmethod
from tools import Storage
from logger import get_logger

logger = get_logger(__name__)

class ConfigBase(object):
    def __init__(self):
        self._subscribers = []

    def on_change(self, handler):
        self._subscribers.append(handler)
        return self

    def notify(self, new, old):
        for handler in self._subscribers:
            handler(new, old)
        return self

class ConfigValue(ConfigBase):
    def __init__(self, value):
        ConfigBase.__init__(self)
        self.value = value

    def __repr__(self):
        return str(self.value)

class ConfigNode(dict, ConfigBase):
    def __init__(self, *args, **kwargs):
        ConfigBase.__init__(self)
        dict.__init__(self, *args, **kwargs)

    def sub_values(self):
        subs = dict()
        for name in self:
            val = self[name]
            if type(val) is ConfigNode:
                subs[name] = val.sub_values()
            else:
                subs[name] = val.value
        return subs

class Config(object):

    def __init__(self, file_reader):
        self.data = Storage()
        self.file_reader = file_reader

    def load(self, file_name):
        self.file_name = file_name
        return self.parse()

    def reload(self):
        self.old_data = self.data
        if not self.parse():
            return False

        logger.info('Reloading the config')

        def check_eq(new_node, old_node):

            new_node._subscribers = old_node._subscribers

            res = False

            if type(new_node) is ConfigNode and type(old_node) is ConfigNode:

                # common nodes in new_node and new_node
                common = []
                # get new nodes in new_node dict
                for name in new_node:
                    if name in old_node:
                        common.append(name)
                    else:
                        new_node.notify(name, None) #...
                for name in old_node:
                    if name not in new_node:
                        old_node.notify(None, name)

                for name in common:
                    res = res or check_eq(new_node[name], old_node[name])

                if res:
                    new_node.notify(new_node, old_node)

            elif type(new_node.value) is list and type(old_node.value) is list:
                if len(new_node.value) != len(old_node.value):
                    new_node.notify(new_node, old_node) #jeeeeeeeeeeeeeej
                    res = True
            else:
                if new_node.value != old_node.value:
                    new_node.notify(new_node, old_node) #jeeeeeeeeeeeeeej
                    res = True

            return res

        check_eq(self.data, self.old_data)

    def parse(self):

        content = self.file_reader.read_all(self.file_name)

        data = ConfigNode(json.loads(content))

        def iter(node):
            for name in node:
                val = node[name]
                if type(val) is dict:
                    node[name] = ConfigNode(node[name])
                    iter(node[name])
                else:
                    node[name] = ConfigValue(node[name])

        iter(data)
        self.data = data

        return True