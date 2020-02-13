from econokindle.TagParser import TagParser


class IParser(TagParser):

    def parse(self, item: dict) -> dict:
        return {
            'open': '<em>',
            'close': '</em>',
        }
