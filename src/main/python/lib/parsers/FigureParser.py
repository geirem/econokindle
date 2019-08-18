from lib.TagParser import TagParser


class FigureParser(TagParser):

    def parse(self, tag: dict) -> dict:
        children = tag['children']
        if children is None or len(children) == 0:
            return {
                'open': '',
                'close': '',
            }
        return super().parse(tag)

