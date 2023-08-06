import logging
import logging.config

import json

def load_logger(config_file_name):
    with open(config_file_name) as f:
        logging.config.dictConfig(json.load(f))

def get_logger(name, module = None):
    logger = logging.getLogger('%s.%s' % (module, name) if module else name)
    return logger

class StdWriter(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.msg = ''

    def write(self, text):
        if text.startswith('\n'):
            self.logger.log(self.level, self.msg)
            self.msg = ''
        self.msg += text
