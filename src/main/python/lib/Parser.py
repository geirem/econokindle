from typing import Optional


class Parser:

    def __init__(self, script: dict):
        for item in [0, 1, 2, 3, 4, 5]:
            if 'canonical' in script[item]['response']:
                self.__script = script[item]['response']['canonical']
                break
        self.__images = []
        self.__parsed_elements = []

    def __extract_main_image(self) -> Optional[str]:
        if 'image' in self.__script:
            if 'main' in self.__script['image']:
                if 'url' in self.__script['image']['main']:
                    if 'canonical' in self.__script['image']['main']['url']:
                        return self.__script['image']['main']['url']['canonical']

    def __find_text_data(self) -> Optional[str]:
        for item in self.__script:
            if item.startswith('_text'):
                return item

    def parse(self) -> dict:
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
            image = image.split('/').pop()
        result = {
            'title': self._apply_html_entities(headline),
            'text': self._apply_html_entities(''.join(self.__parsed_elements)),
            'section': self._apply_html_entities(section),
            'subheadline': self._apply_html_entities(subheadline),
            'description': self._apply_html_entities(description),
            'dateline': self._apply_html_entities(dateline),
            'image': image,
            'images': self.__images,
        }
        return result

    @staticmethod
    def _get_response(script: dict, index: int, field: str) -> Optional[dict]:
        if len(script) - 1 < index:
            return None
        if 'response' not in script[index]:
            return None
        if field not in script[index]['response']:
            return None
        return script[index]['response'][field]

    def _parse_html(self, element: dict) -> None:
        for item in element:
            try:
                self.__parsed_elements.append(item['data'])
            except:
                pass
            if item['type'] != 'tag':
                continue
            tag = self.__parse_tag_type(item)
            children = item['children']
            self.__parsed_elements.append(tag['open'])
            self._parse_html(children)
            self.__parsed_elements.append(tag['close'])

    def __parse_tag_type(self, item: dict) -> dict:
        tag_name = item['name']
        tag = {
            'name': tag_name,
            'open': '<' + tag_name + '>',
            'close': '</' + tag_name + '>',
        }
        attributes = item['attribs']
        if tag_name == 'span':
            if 'data-caps' in attributes and attributes['data-caps'] == 'initial':
                tag['open'] = '<span class="dropcaps">'
        if tag_name == 'br':
            tag['open'] = ''
            tag['close'] = ''
        if tag_name == 'img':
            src = attributes['src']
            name = src.split('/').pop()
            self.__images.append(src)
            tag['open'] = '<img alt="" src="' + name + '"/>'
        return tag

    @staticmethod
    def _apply_html_entities(processed: str) -> str:
        return processed.encode(encoding="ascii", errors="xmlcharrefreplace").decode("utf-8")
