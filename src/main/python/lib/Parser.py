from typing import Optional

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
        self.TAG_PARSERS = {
            'span': self.__parse_span,
            'img': self.__parse_img,
            'br': self.__parse_br,
            'iframe': self.__parse_iframe,
            'a': self.__parse_a,
            'h2': self.__parse_h2,
        }

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
                tag = self.TAG_PARSERS.get(item['name'], self.__parse__default)(item)
                self.__parsed_elements.append(tag['open'])
                self.__parse_article_body(item['children'])
                self.__parsed_elements.append(tag['close'])

    def __parse_a(self, item: dict) -> dict:
        attributes = item['attribs']
        href = self.__key_creator.key(attributes['href'])
        # Hack to support references to articles in other issues.
        tag = { 'close': '</a>'}
        if href in self.__valid_references:
            tag['open'] = f'<a href="#{href}">'
        else:
            href = attributes['href']
            tag['open'] = f'<a href="{href}">online '
        return tag

    # noinspection PyUnusedLocal
    @staticmethod
    def __parse_br(item: dict) -> dict:
        return {
            'open': '<br/>',
            'close': '',
        }

    # noinspection PyUnusedLocal
    @staticmethod
    def __parse__default(item: dict) -> dict:
        name = item['name']
        return {
            'open': '<' + name + '>',
            'close': '</' + name + '>',
        }

    # noinspection PyUnusedLocal
    @staticmethod
    def __parse_iframe(item: dict) -> dict:
        return {
            'open': '',
            'close': '',
        }

    @staticmethod
    def __parse_span(item: dict) -> dict:
        attributes = item['attribs']
        if 'data-caps' in attributes and attributes['data-caps'] == 'initial':
            return {
                'open': '<span class="dropcaps">',
                'close': '</span>',
            }
        return {
            'open': '<span>',
            'close': '</span>',
        }

    @staticmethod
    # noinspection PyUnusedLocal
    def __parse_h2(item: dict) -> dict:
        return {
            'open': '<h2 class="subheader">',
            'close': '</h2>',
        }

    def __parse_img(self, item: dict) -> dict:
        attributes = item['attribs']
        src = attributes['src']
        name = self.__key_creator.key(src)
        self.__images.append(src)
        height = attributes['height']
        width = attributes['width']
        return {
            'open': f'<img alt="" src="{name}" height="{height}" width="{width}"/>',
            'close': '',
        }

    @staticmethod
    def __apply_html_entities(processed: Optional[str]) -> str:
        if processed is None:
            return ''
        return processed.encode(encoding='ascii', errors='xmlcharrefreplace').decode('utf-8')
