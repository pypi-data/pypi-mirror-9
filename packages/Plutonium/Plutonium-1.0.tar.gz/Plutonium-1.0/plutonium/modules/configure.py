
import os
import json
import pip
import shutil
import logging
import glob
import imp
import re
from plutonium.directories import Directory
from plutonium.modules.logger import load_logger

def edit_json_file(func):

    def wrapper(*args):
        args = [arg for arg in args]

        # first param is the filename
        with open(args[1], 'r+') as f:
            data = json.load(f)

            args[1] = data

            func(*args)

            f.seek(0, 0)
            f.write(json.dumps(data, indent = 4, separators = (',', ': ')))

    return wrapper

class Configure():

    def __init__(self):

        self.conf_dir = Directory.config()

        self.copy_default_configs()

        self.app_config = os.path.join(self.conf_dir, 'core.json')
        self.logger_config = os.path.join(self.conf_dir, 'logger.json')

        self.configure_logger_config(self.logger_config)

        # no we have logger config, time to use it...
        load_logger(self.logger_config)

        self.logger = logging.getLogger('init')

        self.logger.info("Configuring Plutonium")

        if len(self.new_files):
            self.logger.info("Example config files has been copied to %s" % self.conf_dir)

        self.configure_app_config(self.app_config)

        self.upgrade_database()

    def copy_default_configs(self):
        # create config dir
        if not os.path.isdir(self.conf_dir):
            os.makedirs(self.conf_dir)

        source_dir = Directory.example_configs()

        # copy example configs
        self.new_files = []
        for filename in glob.glob(os.path.join(source_dir, '*.*')):
            dst = os.path.join(self.conf_dir, os.path.basename(filename))
            if not os.path.isfile(dst):
                shutil.copy(filename, dst)
                self.new_files.append(dst)

    @edit_json_file
    def configure_logger_config(self, data):

        if self.logger_config in self.new_files:
            data['handlers']['file']['filename'] = os.path.join(Directory.base(), 'plutonium.log')

    @edit_json_file
    def configure_app_config(self, data):
        self.logger.info("Configuring app config")

        if self.app_config in self.new_files:
            data['database']['url'] = 'sqlite:///%s' % os.path.join(Directory.base(), 'plutonium.db')
            self.logger.debug("Default database uri is set to '%s'" % data['database']['url'])

        # searching for plutonium plugins and configure the app config's plugins section
        for pkg in pip.get_installed_distributions():
            res = re.match('^plutonium\-plugin\-([a-z0-9]{1,})\-([a-z0-9]{1,})$', pkg.key)
            if not res:
                continue

            type = res.group(1)
            name = res.group(2)

            path = os.path.join(pkg.location, 'plutonium_plugin_%s_%s' % (type, name), 'plugin_config.py')

            if not os.path.isfile(path):
                self.logger.debug("Plugin config not found for '%s'. Maybe this is not a Plutonium plugin?" % pkg.key)
                continue

            plugin_config = imp.load_source('data', path).data

            if type not in data['plugins']:
                data['plugins'][type] = dict()

            if name not in data['plugins'][type]:
                data['plugins'][type][name] = plugin_config
                self.logger.info("Configuring '%s' plugin" % pkg.key)

    def upgrade_database(self):
        self.logger.info("Upgrading the database")

        from plutonium.modules.config import Config
        from plutonium.modules.tools import FileReader
        from alembic.config import Config as AlembicConfig
        from alembic import command

        config = Config(FileReader())
        config.load(self.app_config)

        alembic_cfg = AlembicConfig()
        alembic_cfg.set_main_option('script_location', os.path.realpath(os.path.join(Directory.module_base(), 'alembic')))
        alembic_cfg.set_main_option('sqlalchemy.url', config.data['database']['url'].value)

        command.upgrade(alembic_cfg, "head")
