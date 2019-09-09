import importlib
import os
import pkgutil

from econokindle import KeyCreator
from econokindle.TagParser import TagParser


class ParsingStrategy:

    def __init__(self, key_creator: KeyCreator, valid_references: list, images: list):
        self.__parsers = {}
        for (_, name, _) in pkgutil.iter_modules([os.path.dirname(__file__) + '/parsers']):
            imported_module = importlib.import_module('.' + name, package='econokindle.parsers')
            clazz_name = list(filter(lambda x: x != 'TagParser' and not x.startswith('__'), dir(imported_module)))[0]
            clazz = getattr(imported_module, clazz_name)
            self.__parsers[self.__key_from_name(clazz_name)] = clazz(key_creator, images, valid_references)
        self.__default_parser = TagParser(key_creator, images, valid_references)

    @staticmethod
    def __key_from_name(name: str) -> str:
        return name.replace('Parser', '').lower()

    def get_parser(self, tag: dict) -> TagParser:
        return self.__parsers.get(tag['name'], self.__default_parser)
