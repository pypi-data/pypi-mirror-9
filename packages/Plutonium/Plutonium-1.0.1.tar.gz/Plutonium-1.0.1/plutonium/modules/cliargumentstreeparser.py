
import argparse

from tools import Storage

class CLIArgumentsTreeParser(object):

    def __init__(self, config, root_name):
        self.parser = argparse.ArgumentParser()
        self.config = config
        self.root_name = root_name

    def build(self, parser, node, node_name):
        subparsers = parser.add_subparsers(dest=node_name)

        for item in node:
            subparser = subparsers.add_parser(item['name'], **item['desc'])

            if 'subcommands' in item:
                self.build(subparser, item['subcommands'], item['name'])

            elif 'arguments' in item:
                for name in item['arguments']:
                    subparser.add_argument(name, **item['arguments'][name])

    def parse(self):
        self.build(self.parser, self.config, self.root_name)

        self.raw_data = vars(self.parser.parse_args())

        self.data = Storage()

        self.structuring(self.root_name, self.data)

        return self.data

    def structuring(self, name, result, nodes = []):
        if name in self.raw_data:
            nodes.append(name)
            result.name = name
            if len(self.raw_data) > len(nodes):
                result.sub = Storage()
                self.structuring(self.raw_data[name], result.sub, nodes)
            else:
                result.sub = Storage(name = self.raw_data[name])
        else:
            result.name = name
            result.args = Storage()
            for dname in self.raw_data:
                if dname not in nodes:
                    result.args[dname] = self.raw_data[dname]
