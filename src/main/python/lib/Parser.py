from typing import Optional

from jsonpath_rw import parse

from lib import KeyCreator


class Parser:

    def __init__(self, script: dict, key_creator: KeyCreator):
        self.__script = parse('[*].response.canonical').find(script).pop().value
        self.__images = []
        self.__parsed_elements = []
        self.__key_creator = key_creator
        self.__url_path = parse('image.main.url.canonical')

    def __extract_main_image(self) -> Optional[str]:
        url = self.__url_path.find(self.__script)
        if len(url) == 1:
            return url.pop().value
        return None

    def __find_text_data(self) -> Optional[str]:
        for item in self.__script:
            if item.startswith('_text'):
                return item

    def parse(self) -> dict:
        article_id = self.__key_creator.key(self.__script['url']['canonical'])
        image = self.__extract_main_image()
        text_field = self.__find_text_data()
        section = self.__script['print']['section']['headline']
        headline = self.__script['headline']
        subheadline = self.__script['subheadline']
        description = self.__script['description']
        dateline = self.__script['dateline']
        if dateline is None:
            dateline = ''
        self._parse_html(self.__script[text_field])
        if image:
            self.__images.append(image)
            image = self.__key_creator.key(image)
        result = {
            'title': self._apply_html_entities(headline),
            'text': self._apply_html_entities(''.join(self.__parsed_elements)),
            'section': self._apply_html_entities(section),
            'subheadline': self._apply_html_entities(subheadline),
            'description': self._apply_html_entities(description),
            'dateline': self._apply_html_entities(dateline),
            'image': image,
            'images': self.__images,
            'id': article_id,
        }
        return result

    def _parse_html(self, element: dict) -> None:
        for item in element:
            if item['type'] == 'text':
                self.__parsed_elements.append(item['data'])
            elif item['type'] == 'tag':
                tag = self.__parse_tag_type(item)
                self.__parsed_elements.append(tag['open'])
                self._parse_html(item['children'])
                self.__parsed_elements.append(tag['close'])

    def __parse_tag_type(self, item: dict) -> dict:
        name = item['name']
        tag = {
            'name': name,
            'open': '<' + name + '>',
            'close': '</' + name + '>',
        }
        attributes = item['attribs']
        if name == 'a':
            href = self.__key_creator.key(attributes['href'])
            tag['open'] = f'<a href="#{href}">'
        if name == 'span':
            if 'data-caps' in attributes and attributes['data-caps'] == 'initial':
                tag['open'] = '<span class="dropcaps">'
        if name == 'br':
            tag['open'] = ''
            tag['close'] = ''
        if name == 'img':
            src = attributes['src']
            name = self.__key_creator.key(src)
            self.__images.append(src)
            tag['open'] = '<img alt="" src="' + name + '" height="' + attributes['height'] + '" width="' + attributes['width'] + '"/>'
            tag['close'] = ''
        return tag

    @staticmethod
    def _apply_html_entities(processed: str) -> str:
        return processed.encode(encoding='ascii', errors='xmlcharrefreplace').decode('utf-8')
