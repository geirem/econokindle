from typing import Optional

from jsonpath_rw import parse

from lib import KeyCreator


class Parser:

    def __init__(self, script: dict, key_creator: KeyCreator, valid_references: list):
        self.__script = parse('[*].response.canonical').find(script).pop().value
        self.__images = []
        self.__parsed_elements = []
        self.__key_creator = key_creator
        self.__url_path = parse('image.main.url.canonical')
        self.__valid_references = valid_references

    def __extract_main_image(self) -> Optional[str]:
        url = self.__url_path.find(self.__script)
        if len(url) == 1:
            return url.pop().value
        return None

    def __find_text_data(self) -> dict:
        for item in self.__script:
            if item.startswith('_text'):
                return self.__script[item]

    def _start_body_parsing(self) -> None:
        for item in self.__script:
            if item.startswith('_text'):
                self.__parse_article_body(self.__script[item])
                return

    def parse(self) -> dict:
        article_id = self.__key_creator.key(self.__script['url']['canonical'])
        image = self.__extract_main_image()
        self._start_body_parsing()
        if image:
            self.__images.append(image)
            image = self.__key_creator.key(image)
        result = {
            'title': self._apply_html_entities(self.__script['headline']),
            'text': self._apply_html_entities(''.join(self.__parsed_elements)),
            'section': self._apply_html_entities(self.__script['print']['section']['headline']),
            'subheadline': self._apply_html_entities(self.__script['subheadline']),
            'description': self._apply_html_entities(self.__script['description']),
            'dateline': self._apply_html_entities(self.__script['dateline']),
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
                tag = self.__parse_tag_type(item)
                self.__parsed_elements.append(tag['open'])
                self.__parse_article_body(item['children'])
                self.__parsed_elements.append(tag['close'])

    def __parse_tag_type(self, item: dict) -> dict:
        name = item['name']
        tag = {
            'open': '<' + name + '>',
            'close': '</' + name + '>',
        }
        attributes = item['attribs']
        if name == 'iframe':
            return {'open': '', 'close': ''}
        if name == 'a':
            href = self.__key_creator.key(attributes['href'])
            # Hack to support references to articles in other issues.
            if href in self.__valid_references:
                tag['open'] = f'<a href="#{href}">'
            else:
                href = attributes['href']
                tag['open'] = f'<a href="{href}">online '
        if name == 'span':
            return self.__parse_span(item)
        if name == 'br':
            return self.__parse_br(item)
        if name == 'img':
            return self.__parse_img(item)
        return tag

    @staticmethod
    def _apply_html_entities(processed: Optional[str]) -> str:
        if processed is None:
            return ''
        return processed.encode(encoding='ascii', errors='xmlcharrefreplace').decode('utf-8')

    # noinspection PyUnusedLocal
    @staticmethod
    def __parse_br(item: dict) -> dict:
        return {
            'open': '<br/>',
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

    def __parse_img(self, item: dict) -> dict:
        attributes = item['attribs']
        src = attributes['src']
        name = self.__key_creator.key(src)
        self.__images.append(src)
        return {
            'open': '<img alt="" src="' + name + '" height="' + attributes['height'] + '" width="' + attributes['width'] + '"/>',
            'close': '',
        }
