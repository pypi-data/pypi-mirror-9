
import os

class Directory(object):

    @staticmethod
    def base():
        return os.path.join(os.path.expanduser('~'), '.plutonium')

    @staticmethod
    def config():
        return os.path.join(Directory.base(), 'config')

    @staticmethod
    def module_base():
        return os.path.realpath(os.path.dirname(__file__))

    @staticmethod
    def example_configs():
        return os.path.join(Directory.module_base(), 'example_configs')