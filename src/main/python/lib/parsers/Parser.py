# Not threadsafe.
from typing import Optional


class Parser:

    def __init__(self, script: dict, images: list):
        self._script = script
        self._images = images

    @staticmethod
    def _get_response(script: dict, index: int, field: str) -> Optional[dict]:
        if len(script) - 1 < index:
            return None
        if 'response' not in script[index]:
            return None
        if field not in script[index]['response']:
            return None
        return script[index]['response'][field]

    def parse(self) -> dict:
        raise Exception

    @staticmethod
    def wants(script: dict) -> Optional[dict]:
        raise Exception

    def _parse_html(self, article_string: dict, images: list) -> str:
        result = ''
        for item in article_string:
            try:
                result += item['data']
            except:
                pass
            if item['type'] not in ['tag', 'html-tag']:
                continue
            tag = item['name']
            if tag == 'img':
                attributes = item['attribs']
                src = attributes['src']
                name = src.split('/').pop()
                images.append(src)
                result += '<img alt="" src="' + name + '" height="' + attributes['height'] + '" width="' + attributes['width'] + '"/>'
                continue
            children = item['children']
            if tag == 'span':
                result += self._parse_html(children, images)
                continue
            result += '<' + tag + '>' + self._parse_html(children, images) + '</' + tag + '>'
        return result

    @staticmethod
    def _apply_html_entities(processed: str) -> str:
        return processed.encode(encoding="ascii", errors="xmlcharrefreplace").decode("utf-8")
