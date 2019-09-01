from lib import KeyCreator
from lib.TagParser import TagParser


class PParser(TagParser):

    def parse(self, item: dict) -> dict:
        return super().parse(item)
