from lib.TagParser import TagParser


class FigureParser(TagParser):

    def parse(self, tag: dict) -> dict:
        if self._peek_at_first_child(tag) is None:
            return {
                'open': '',
                'close': '',
            }
        return super().parse(tag)
