from econokindle.TagParser import TagParser


class ImgParser(TagParser):

    def parse(self, tag: dict) -> dict:
        attributes = tag['attribs']
        src = attributes['src']
        name = self._key_creator.key(src)
        self._images.append(src)
        height = f'height="{attributes["height"]}"' if 'height' in attributes else ''
        width = f'width="{attributes["width"]}"' if 'width' in attributes else ''
        return {
            'open': f'<img alt="" src="{name}" {height} {width}"/>',
            'close': '',
        }
