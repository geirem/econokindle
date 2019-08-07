from typing import Optional

from lib.parsers.Parser import Parser


class NullParser(Parser):

    def __init__(self, script: dict, images: list):
        super().__init__(script, images)

    # noinspection PyMethodMayBeStatic
    def parse(self) -> dict:
        return {}

    @staticmethod
    def wants(script: dict) -> Optional[dict]:
        return {}
