from lib.TagParser import TagParser


class BrParser(TagParser):

    # noinspection PyUnusedLocal
    def parse(self, tag: dict) -> dict:
        return {
            'open': '<br/>',
            'close': '',
        }
