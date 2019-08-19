from lib.TagParser import TagParser


class FigureParser(TagParser):

    def parse(self, tag: dict) -> dict:
        if self._look_at_next_tag(tag) is None:
            return {
                'open': '',
                'close': '',
            }
        return super().parse(tag)
