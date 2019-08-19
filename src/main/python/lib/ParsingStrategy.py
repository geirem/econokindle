
from lib.TagParser import TagParser
from lib.parsers.SpanParser import SpanParser
from lib.parsers.ImgParser import ImgParser
from lib.parsers.BrParser import BrParser
from lib.parsers.IframeParser import IframeParser
from lib.parsers.H2Parser import H2Parser
from lib.parsers.FigureParser import FigureParser
from lib.parsers.AParser import AParser

from lib import KeyCreator


class ParsingStrategy:

    def __init__(self, key_creator: KeyCreator, valid_references: list, images: list):
        self.__images = images
        self.__key_creator = key_creator
        self.__valid_references = valid_references
        self.__parsers = {
            'span': SpanParser(key_creator, self.__images, valid_references),
            'img': ImgParser(key_creator, self.__images, valid_references),
            'br': BrParser(key_creator, self.__images, valid_references),
            'iframe': IframeParser(key_creator, self.__images, valid_references),
            'a': AParser(key_creator, self.__images, valid_references),
            'h2': H2Parser(key_creator, self.__images, valid_references),
            'figure': FigureParser(key_creator, self.__images, valid_references),
        }
        self.__default_parser = TagParser(key_creator, self.__images, valid_references)

    def get_parser(self, tag: dict) -> TagParser:
        return self.__parsers.get(tag['name'], self.__default_parser)
