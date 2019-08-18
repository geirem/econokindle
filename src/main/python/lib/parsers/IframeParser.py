from lib.TagParser import TagParser


class IframeParser(TagParser):

    # noinspection PyUnusedLocal
    def parse(self, tag: dict) -> dict:
        return {
            'open': '',
            'close': '',
        }
