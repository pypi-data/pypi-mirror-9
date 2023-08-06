
from abc import abstractmethod

class PluginBase(object):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def reload(self):
        pass


class OutputPluginBase(PluginBase):

    @abstractmethod
    def send(self, torrent):
        pass

    @abstractmethod
    def get_required_params_struct(self):
        pass

class ConfigUserInterfacePluginBase(PluginBase):
    pass



# TODO: there is any meaning for this class?
class PluginException(Exception):
    pass

class BadPluginException(PluginException):
    pass

class PluginNotFoundException(PluginException):
    pass