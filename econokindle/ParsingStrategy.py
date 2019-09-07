import importlib
import inspect

from econokindle import Article, Issue
from econokindle.TagParser import TagParser


class ParsingStrategy:

    def __init__(self, issue: Issue, article: Article):
        self.__parsers = {}
        try:
            module = importlib.import_module('econokindle.parsers')
            for x in dir(module):
                attribute = getattr(module, x)
                if inspect.isclass(attribute) and issubclass(attribute, TagParser) and attribute is not TagParser:
                    parser = attribute(issue, article)
                    self.__parsers[parser.supports()] = parser
        except ImportError:
            pass
        self.__default_parser = TagParser(issue, article)

    def get_parser(self, tag: dict) -> TagParser:
        return self.__parsers.get(tag['name'], self.__default_parser)
