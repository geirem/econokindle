from lib.TagParser import TagParser


class ImgParser(TagParser):

    def parse(self, tag: dict) -> dict:
        attributes = tag['attribs']
        src = attributes['src']
        name = self._key_creator.key(src)
        self._images.append(src)
        height = attributes['height']
        width = attributes['width']
        return {
            'open': f'<img alt="" src="{name}" height="{height}" width="{width}"/>',
            'close': '',
        }
