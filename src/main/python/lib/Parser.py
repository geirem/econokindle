from typing import Optional


class Parser:

    def __init__(self, script: dict):
        for item in [0, 1, 2, 3, 4, 5]:
            if 'canonical' in script[item]['response']:
                self._script = script[item]['response']['canonical']
                break
        self._images = []

    def __extract_main_image(self) -> Optional[str]:
        if 'image' in self._script:
            if 'main' in self._script['image']:
                if 'url' in self._script['image']['main']:
                    if 'canonical' in self._script['image']['main']['url']:
                        return self._script['image']['main']['url']['canonical']

    def __find_text_data(self) -> Optional[str]:
        for item in self._script:
            if item.startswith('_text'):
                return item

    def parse(self) -> dict:
        image = self.__extract_main_image()
        text_field = self.__find_text_data()
        section = self._script['print']['section']['headline']
        headline = self._script['headline']
        subheadline = self._script['subheadline']
        description = self._script['description']
        dateline = self._script['dateline']
        if dateline is None:
            dateline = ''
        text = self._parse_html(self._script[text_field], self._images)
        if image:
            self._images.append(image)
            image = image.split('/').pop()
        result = {
            'title': self._apply_html_entities(headline),
            'text': self._apply_html_entities(text),
            'section': self._apply_html_entities(section),
            'subheadline': self._apply_html_entities(subheadline),
            'description': self._apply_html_entities(description),
            'dateline': self._apply_html_entities(dateline),
            'image': image,
            'images': self._images,
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
            if tag == 'span' or tag == 'br':
                result += self._parse_html(children, images)
                continue
            result += '<' + tag + '>' + self._parse_html(children, images) + '</' + tag + '>'
        return result

    @staticmethod
    def _apply_html_entities(processed: str) -> str:
        return processed.encode(encoding="ascii", errors="xmlcharrefreplace").decode("utf-8")
