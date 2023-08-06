import os
import shutil
import glob
import pyjsonrpc
import traceback

from tools import SimpleResponse, URLLoader
from commands import CommandRequestHandler, external_jsonrpc_command, commandline
from fetcher import Fetcher
from plutonium.plugins.plugin_manager import PluginManager, PluginLoader
from orm.manager import Manager
from orm.base import Base


from plutonium.modules.logger import get_logger
logger = get_logger(__name__)

class Plutonium(object):
    """
        The handler class of the core Plutonium
    """

    def __init__(self, config):
        self.config = config
        self.url_loader = URLLoader()
        self.init_callbacks = []

    @external_jsonrpc_command
    @commandline('Database related commands', dict(command = dict(help='Command', type = str, choices = ['clean', 'purge'])))
    def database(self, command):
        if command == 'clean':
            pass

        elif command == 'purge':
            try:
                self.orm_manager.close_sessions()

                engine = self.orm_manager.get_engine()

                logger.debug("Drop all the tables!")

                for table in reversed(Base.metadata.sorted_tables):
                    logger.debug("Dropping table %s..." % table.name)
                    table.drop(engine)

                engine.execute('DROP TABLE `alembic_version`')

                logger.debug("All table has been dropped")

                return SimpleResponse(True, "The database has been fully purged")

            except Exception as e:
                logger.exception(e)
                return SimpleResponse(False, str(e))

        return SimpleResponse(True)

    # initialize all of the required stuffs for the Plutonium core
    @external_jsonrpc_command
    def init(self):
        try:
            # init plugins
            self.plugin_manager = PluginManager(PluginLoader('plugins', self))
            self.plugin_manager.load(self.config.data['plugins'])

        except Exception as e:
            logger.error(traceback.format_exc())
            return SimpleResponse(False, 'Exception occured during the plugin initalization: ' + str(e))

        try:
            # import orm related manager
            self.orm_manager = Manager(self.config.data)

        except Exception as e:
            logger.error(traceback.format_exc())
            return SimpleResponse(False, 'Exception occured during the database initalization: ' + str(e))

        try:
            self.fetcher = Fetcher(self.config, self.orm_manager, self.plugin_manager)
            self.fetcher.init_models()
            self.fetcher.fetch_feeds_from_database()
            self.fetcher.start()
            CommandRequestHandler.externals.append(self.fetcher)

        except Exception as e:
            logger.error(traceback.format_exc())
            return SimpleResponse(False, 'Exception occured during the fetcher initalization: ' + str(e))

        for callback in self.init_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(traceback.format_exc())
                return SimpleResponse(False, 'Exception occured during calling the init callback:' + str(e))

        return SimpleResponse(True)

    def register_after_successfully_init(self, callback):
        self.init_callbacks.append(callback)

    # Initialize the command server to receive IPC commands.
    def start_command_server(self):
        try:
            command_server_address = self.config.data['command_server']
            self.command_server = pyjsonrpc.ThreadingHttpServer(
                server_address = (command_server_address['host'].value, command_server_address['port'].value),
                RequestHandlerClass = CommandRequestHandler
            )
        except Exception as e:
            logger.error('Exception occured during the command server initalization: ' + str(e) + traceback.format_exc())
            return

        CommandRequestHandler.externals.append(self)

        self.command_server.serve_forever()

    @external_jsonrpc_command
    @commandline('Reload the config')
    def reload(self):
        try:
            self.config.reload()
        except Exception as e:
            logger.error(traceback.format_exc())
            return SimpleResponse(False, 'Exception occured during config parsing: ' + str(e))

        return SimpleResponse(True)
