import importlib

from plutonium.modules.tools import ucfirst
from functools import partial

from plugin import PluginNotFoundException, PluginBase

"""
Manager class for the plugins

expected config structure:
{
    "type_1": {
        "plugin_name_1": {
            "enabled": true,
            "arguments": {...}
        }
    },
    "type_2": {
        "plugin_name_2": {
            "enabled": true,
            "arguments": {...}
        }
    }
}
"""
class PluginManager(object):

    def __init__(self, plugin_loader):
        self.plugin_loader = plugin_loader
        self.plugins = {}

    def get_plugin(self, type, name):
        if type not in self.plugins:
            raise PluginNotFoundException("Unknown type: "+str(type))
        if name not in self.plugins[type]:
            raise PluginNotFoundException("Unknown name ('%s') with type ('%s')" % (str(name), str(type)))

        plugin = self.plugins[type][name]

        if not isinstance(plugin, PluginBase):
            raise BadPluginException('This plugin does not inherited from PluginBase class!')

        return plugin

    def on_plugin_list_change(self, type, new, old):
        if old is None:
            logger.debug('Plugin node appended for type %s, name: %s' % (type, new))

        elif new is None:
            logger.debug('Plugin node disappeared in type %s, name: %s' % (type, old))

        else:
            # some change in deeper of the tree
            pass

    def on_plugin_enabled_change(self, new, old, type, name):
        plugin = self.get_plugin(type, name)
        if new.value:
            plugin.start()
        else:
            plugin.stop()

    def on_plugin_arguments_change(self, type, name, new, old):
        plugin = self.get_plugin(type, name)
        plugin.reload(**new.sub_values())

    def load(self, config):
        for type in config:
            self.plugins[type] = {}
            config[type].on_change(partial(self.on_plugin_list_change, type))
            for name in config[type]:
                desc = config[type][name]
                desc['enabled'].on_change(partial(self.on_plugin_enabled_change, type, name))
                plugin = self.plugin_loader.load(type, name, desc)

                if not isinstance(plugin, PluginBase):
                    raise BadPluginException('This plugin does not inherited from PluginBase class!')

                self.plugins[type][name] = plugin

                # subscribe for arguments's change
                desc['arguments'].on_change(partial(self.on_plugin_arguments_change, type, name))

                if desc['enabled'].value:
                    plugin.start()


class PluginLoader(object):

    def __init__(self, base_dir, plutonium):
        self.base_dir = base_dir
        self.plutonium = plutonium

    def load(self, type, name, descriptor):

        # get the module name from the base dir, the plugin's type and name
        # eg: plugins.config_user_interface.web
        #path = '.'.join([self.base_dir, type, name, 'plugin'])
        path = 'plutonium_plugin_%s_%s' % (type, name)
        module = importlib.import_module(path)

        # get the plugin classname from the name and the type
        # eg: WebConfigUserInterfacePlugin
        class_name = ucfirst(name) + ''.join([ucfirst(type_part) for type_part in type.split('_')]) + 'Plugin'
        class_type = getattr(module, class_name)

        args = descriptor['arguments'].sub_values()
        args['plutonium'] = self.plutonium

        # create a new instance from the plugin
        return class_type(**args)

