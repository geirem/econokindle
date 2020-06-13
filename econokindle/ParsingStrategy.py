import importlib

from econokindle import KeyCreator
from econokindle.TagParser import TagParser


class ParsingStrategy:

    def __init__(self, key_creator: KeyCreator, valid_references: list, images: list):
        self._parsers = {}
        self._key_creator = key_creator
        self._valid_references = valid_references
        self._images = images
        self._default_parser = TagParser(key_creator, images, valid_references)

    def get_parser(self, tag: dict) -> TagParser:
        if (name := tag['name']) not in self._parsers:
            try:
                clazz_name = f"{name.capitalize()}Parser"
                imported_module = importlib.import_module(f'econokindle.parsers.{clazz_name}')
                clazz = getattr(imported_module, clazz_name)
                self._parsers[name] = clazz(self._key_creator, self._images, self._valid_references)
            except ModuleNotFoundError:
                self._parsers[name] = self._default_parser
        return self._parsers.get(name)
