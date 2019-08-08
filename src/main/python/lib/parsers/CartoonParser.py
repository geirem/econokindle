from typing import Optional
from lib.parsers.Parser import Parser


class CartoonParser(Parser):

    INDEX = 2
    FIELD = 'content'

    def __init__(self, script: dict, images: list):
        super().__init__(script, images)

    def parse(self):
        image = self._script['mainImageObj']['path']
        self._images.append(self._script['mainImageObj']['path'])
        return {
            'title': Parser._apply_html_entities(self._script['title']),
            'text': '<p><img alt="" src="' + image.split('/').pop() + '"/></p>',
            'section': 'The world this week',
            'subheadline': '',
            'headline': '',
        }

    @staticmethod
    def wants(script: dict) -> Optional[dict]:
        return Parser._get_response(script, CartoonParser.INDEX, CartoonParser.FIELD)
