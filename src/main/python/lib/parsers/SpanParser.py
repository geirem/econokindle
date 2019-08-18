from lib.TagParser import TagParser


class SpanParser(TagParser):

    def parse(self, tag: dict) -> dict:
        attributes = tag['attribs']
        if 'data-caps' in attributes and attributes['data-caps'] == 'initial':
            return {
                'open': '<span class="dropcaps">',
                'close': '</span>',
            }
        return super().parse(tag)
