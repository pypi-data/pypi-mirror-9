from .type_json import JsonFinder
from .type_yaml import YamlFinder
from .type_ini import IniFinder


class ConfigFinder(object):

    def __init__(self):
        self.finders = [JsonFinder(), YamlFinder(), IniFinder()]

    def find_module(self, fullname, path=None):
        for finder in self.finders:
            loader = finder.find_module(fullname, path)
            if loader is not None:
                return loader
        return None
