
from econokindle.TagParser import TagParser
from econokindle.parsers.SpanParser import SpanParser
from econokindle.parsers.ImgParser import ImgParser
from econokindle.parsers.BrParser import BrParser
from econokindle.parsers.PParser import PParser
from econokindle.parsers.IframeParser import IframeParser
from econokindle.parsers.H2Parser import H2Parser
from econokindle.parsers.FigureParser import FigureParser
from econokindle.parsers.AParser import AParser

from econokindle import KeyCreator


class ParsingStrategy:

    def __init__(self, key_creator: KeyCreator, valid_references: list, images: list):
        self.__images = images
        self.__key_creator = key_creator
        self.__external_articles = []
        self.__parsers = {
            'span': SpanParser(key_creator, self.__images, valid_references, self.__external_articles),
            'img': ImgParser(key_creator, self.__images, valid_references, self.__external_articles),
            'br': BrParser(key_creator, self.__images, valid_references, self.__external_articles),
            'iframe': IframeParser(key_creator, self.__images, valid_references, self.__external_articles),
            'a': AParser(key_creator, self.__images, valid_references, self.__external_articles),
            'h2': H2Parser(key_creator, self.__images, valid_references, self.__external_articles),
            'p': PParser(key_creator, self.__images, valid_references, self.__external_articles),
            'figure': FigureParser(key_creator, self.__images, valid_references, self.__external_articles),
        }
        self.__default_parser = TagParser(key_creator, self.__images, valid_references, self.__external_articles)

    def get_parser(self, tag: dict) -> TagParser:
        return self.__parsers.get(tag['name'], self.__default_parser)

    def get_external_articles(self):
        return self.__external_articles
