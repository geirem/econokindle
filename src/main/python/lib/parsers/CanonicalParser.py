from typing import Optional

from lib.parsers.Parser import Parser


class CanonicalParser(Parser):

    INDEX = 4
    FIELD = 'canonical'

    def __init__(self, script: dict, images: list):
        super().__init__(script, images)

    def __extract_main_image(self) -> Optional[str]:
        if 'image' in self._script:
            if 'main' in self._script['image']:
                if 'url' in self._script['image']['main']:
                    if 'canonical' in self._script['image']['main']['url']:
                        return self._script['image']['main']['url']['canonical']
        return None

    def __find_text_data(self) -> Optional[str]:
        for item in self._script:
            if item.startswith('_text'):
                return item
        return None

    def parse(self) -> dict:
        image = self.__extract_main_image()
        text_field = self.__find_text_data()
        section = self._script['print']['section']['headline']
        headline = self._script['headline']
        subheadline = self._script['subheadline']
        description = self._script['description']
        text = self._parse_html(self._script[text_field], self._images)
        if image:
            self._images.append(image)
            image = image.split('/').pop()
        result = {
            'title': self._apply_html_entities(headline),
            'text': self._apply_html_entities(text),
            'section': self._apply_html_entities(section),
            'flytitle': self._apply_html_entities(subheadline),
            'subheadline': self._apply_html_entities(subheadline),
            'description': self._apply_html_entities(description),
            'image': image,
        }
        return result

    @staticmethod
    def wants(script: dict) -> Optional[dict]:
        for i in [3, 4, 5]:
            result = Parser._get_response(script, i, CanonicalParser.FIELD)
            if result is None or 'type' not in result:
                continue
            return result
        return result
