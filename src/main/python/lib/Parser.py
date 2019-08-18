from typing import Optional

from lib.TagParser import TagParser
from lib.parsers.SpanParser import SpanParser
from lib.parsers.ImgParser import ImgParser
from lib.parsers.BrParser import BrParser
from lib.parsers.IframeParser import IframeParser
from lib.parsers.H2Parser import H2Parser
from lib.parsers.FigureParser import FigureParser
from lib.parsers.AParser import AParser

from jsonpath_rw import parse

from lib import KeyCreator


class Parser:

    def __init__(self, script: dict, key_creator: KeyCreator, valid_references: list):
        candidates = parse('[*].response.canonical').find(script)
        for candidate in candidates:
            if 'url' in candidate.value:
                self.__script = candidate.value
                break
        self.__images = []
        self.__parsed_elements = []
        self.__key_creator = key_creator
        self.__url_path = parse('image.main.url.canonical')
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

    def __extract_main_image(self) -> Optional[str]:
        url = self.__url_path.find(self.__script)
        if len(url) == 1:
            return url.pop().value
        return None

    def __find_text_data(self) -> dict:
        for item in self.__script:
            if item.startswith('_text'):
                return self.__script[item]

    def __start_body_parsing(self) -> None:
        for item in self.__script:
            if item.startswith('_text'):
                self.__parse_article_body(self.__script[item])
                return

    def parse(self) -> dict:
        article_id = self.__key_creator.key(self.__script['url']['canonical'])
        image = self.__extract_main_image()
        self.__start_body_parsing()
        if image:
            self.__images.append(image)
            image = self.__key_creator.key(image)
        result = {
            'title': self.__apply_html_entities(self.__script['headline']),
            'text': self.__apply_html_entities(''.join(self.__parsed_elements)),
            'section': self.__apply_html_entities(self.__script['print']['section']['headline']),
            'subheadline': self.__apply_html_entities(self.__script['subheadline']),
            'description': self.__apply_html_entities(self.__script['description']),
            'dateline': self.__apply_html_entities(self.__script['dateline']),
            'image': image,
            'images': self.__images,
            'id': article_id,
        }
        return result

    def __parse_article_body(self, element: dict) -> None:
        for item in element:
            if item['type'] == 'text':
                self.__parsed_elements.append(item['data'])
            elif item['type'] == 'tag':
                tag = self.__parsers.get(item['name'], self.__default_parser).parse(item)
                self.__parsed_elements.append(tag['open'])
                self.__parse_article_body(item['children'])
                self.__parsed_elements.append(tag['close'])

    @staticmethod
    def __apply_html_entities(processed: Optional[str]) -> str:
        if processed is None:
            return ''
        return processed.encode(encoding='ascii', errors='xmlcharrefreplace').decode('utf-8')
