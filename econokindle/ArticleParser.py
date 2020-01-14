from typing import Optional, Any

from jsonpath_rw import parse

from econokindle import KeyCreator
from econokindle.DocumentParser import DocumentParser
from econokindle.ParsingStrategy import ParsingStrategy


class ArticleParser(DocumentParser):

    def __init__(self, document: str, key_creator: KeyCreator, issue: dict):
        super().__init__(document, key_creator)
        candidates = parse('props.pageProps.content').find(self._script)
        for candidate in candidates:
            if candidate.value and 'url' in candidate.value:
                self._script = candidate.value
                break
        self.__images = []
        self.__parsed_elements = []
        self.__url_path = parse('image.main.url.canonical')
        self.__parsing_strategy = ParsingStrategy(key_creator, issue['references'], self.__images)

    def __extract_main_image(self) -> Optional[str]:
        url = self.__url_path.find(self._script)
        if len(url) == 1:
            return url.pop().value
        return None

    def __find_text_data(self) -> dict:
        for item in self._script:
            if item.startswith('_text'):
                return self._script[item]

    def __start_body_parsing(self) -> None:
        for item in self._script['text']:
            self.__parse_article_body(item)

    def parse(self) -> dict:
        article_id = self._key_creator.key(self._script['url']['canonical'])
        image = self.__extract_main_image()
        self.__start_body_parsing()
        if image:
            self.__images.append(image)
            image = self._key_creator.key(image)
        if len(self.__parsed_elements) > 0 and '■' not in self.__parsed_elements:
            last_element = self.__parsed_elements.pop()
            self.__parsed_elements.append('<span>■</span>')
            self.__parsed_elements.append(last_element)
        result = {
            'title': self._apply_html_entities(self._script['headline']),
            'text': self._apply_html_entities(''.join(self.__parsed_elements)),
            'section': self._apply_html_entities(self._script['print']['section']['headline']),
            'subheadline': self._apply_html_entities(self._script['subheadline']),
            'description': self._apply_html_entities(self._script['description']),
            'dateline': self._apply_html_entities(self._script['dateline']),
            'image': image,
            'images': self.__images,
            'id': article_id,
        }
        return result

    def __parse_article_body(self, element: Any) -> None:
        if type(element) == dict:
            element = [element]
        for item in element:
            self.__sub_parse(item)

    def __sub_parse(self, element: Any) -> None:
        if element['type'] == 'text':
            self.__parsed_elements.append(element['data'])
        elif element['type'] == 'tag':
            tag = self.__parsing_strategy.get_parser(element).parse(element)
            self.__parsed_elements.append(tag['open'])
            self.__parse_article_body(element['children'])
            self.__parsed_elements.append(tag['close'])
