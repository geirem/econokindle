from typing import Optional

from lib.parsers.Parser import Parser


class ContentParser(Parser):

    INDEX = 4
    FIELD = 'content'

    def __init__(self, script: dict, images: list):
        super().__init__(script, images)

    def parse(self) -> dict:
        content = self._script
        if 'printSectionName' not in content:
            return {}
        section = content['printSectionName']
        if section == 'The world this week' or section == 'Economic and financial indicators':
            return {}
        if 'flyTitle' not in content:
            return {}
        result = {
            'title': self._apply_html_entities(content['title']),
            'text': self._apply_html_entities(self._parse_html(content['html'], self._images)),
            'section': self._apply_html_entities(section),
            'flytitle': self._apply_html_entities(content['flyTitle']),
        }
        return result

    @staticmethod
    def wants(script: dict) -> Optional[dict]:
        result = Parser._get_response(script, ContentParser.INDEX, ContentParser.FIELD)
        if result is None or 'html' not in result:
            return Parser._get_response(script, 3, ContentParser.FIELD)
        return result
