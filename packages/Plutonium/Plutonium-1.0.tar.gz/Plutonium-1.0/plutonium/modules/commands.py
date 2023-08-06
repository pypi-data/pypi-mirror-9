import pyjsonrpc

from tools import SimpleResponse, Storage

from logger import get_logger
logger = get_logger(__name__)

class commandline(object):
    def __init__(self, help, arguments = dict()):
        self.help = help
        self.arguments = arguments

    def __call__(self, func):
        func.commandline = Storage(
            help = self.help,
            arguments = self.arguments
        )

        return func

class CommandRequestHandler(pyjsonrpc.HttpRequestHandler):
    externals = []

    def log_message(self, format, *args):
        # called from parent class...
        logger.debug("HTTP request - %s - %s" % (self.client_address[0], format % args))

    @commandline('Ping')
    @pyjsonrpc.rpcmethod
    def ping(self):
        return SimpleResponse(True, 'pong')

    """
    Example of json rpc method with parameters when should be callable from command line:

    @commandline('paramed test method', dict(teve=dict(help='teveee', type=int), alma=dict(help = 'set the alma', type = int)))
    @pyjsonrpc.rpcmethod
    def paramed(self, alma, teve):
        logger.info('paramed ' + str(alma) + str(teve))
        return SimpleResponse(True, alma*teve)
    """


"""
    This decorator function make an external class's methods to able to called from json rpc client
    For examples see Plutonium class (the order of the decorators are important!)
"""
def external_jsonrpc_command(orig_func):

    def runner(*args, **kwargs):

        ext_obj = None
        for external in CommandRequestHandler.externals:
            if hasattr(external, orig_func.func_name):
               ext_obj = external
               break

        if ext_obj is None:
            return

        # get the original function in the original external class
        func = getattr(ext_obj, orig_func.func_name)

        # need to remove the CommandRequestHandler instance from the beginning of args tuple
        args_list = list(args)
        args_list.pop(0)
        args_tuple = tuple(args_list)

        return func(*args_tuple, **kwargs)

    # add the runner function to CommandRequestHandler by the decorated function name
    setattr(CommandRequestHandler, orig_func.func_name, runner)

    # call the orig decorator
    pyjsonrpc.rpcmethod(runner)

    # need to copy commandline params if exists
    if hasattr(orig_func, 'commandline'):
        runner.commandline = orig_func.commandline

    return orig_func
