
import thread

from timer import Timer
from tools import SimpleResponse, URLLoader
from commands import external_jsonrpc_command, commandline

from plutonium.models.feed import Feed
from plutonium.models.filter import Filter
from plutonium.models.output import Output

from logger import get_logger
logger = get_logger(__name__)

class Fetcher(object):

    def __init__(self, config, orm_manager, plugin_manager):
        self.config = config
        self.orm_manager = orm_manager
        self.plugin_manager = plugin_manager
        self.url_loader = URLLoader()
        self.session = self.orm_manager.create_session()
        self.feeds = []

    def do_fetch(self):
        for feed in self.feeds:
            feed.fetch()

    @external_jsonrpc_command
    @commandline('Fetch the feeds now')
    def fetch(self):
        thread.start_new_thread(self.do_fetch, ())
        return SimpleResponse(True, 'Fetching started in %d feed(s)' % len(self.feeds))

    def add_torrents(self, torrents):
        with self.orm_manager.lock:
            self.session.add_all(torrents)
            self.session.commit()

    def init_models(self):

        # init Output
        if 'output' not in self.plugin_manager.plugins:
            logger.warning('There is no output plugin configured!')
            return

        Output.output_plugins = self.plugin_manager.plugins['output']

    def get_output_types(self):
        if 'output' not in self.plugin_manager.plugins:
            logger.warning('There is no output plugin configured!')
            return

        plugins = self.plugin_manager.plugins['output']

        return plugins.keys()

    def reload(self):
        self.stop()
        self.fetch_feeds_from_database()
        self.start()

    def fetch_feeds_from_database(self):
        self.feeds = []
        enabled_feeds = []

        with self.orm_manager.lock:
            enabled_feeds = self.session.query(Feed).filter_by(enabled = True).all()

        logger.debug("%s enabled feeds has been found" % len(enabled_feeds))

        for feed in enabled_feeds:
            self.feeds.append(feed)
            feed.set_fetcher(self)

    def stop(self):
        for feed in self.feeds:
            feed.stop()

    def start(self):
        for feed in self.feeds:
            feed.start()
