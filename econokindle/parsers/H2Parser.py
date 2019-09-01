from econokindle.TagParser import TagParser


class H2Parser(TagParser):

    def parse(self, tag: dict) -> dict:
        return {
            'open': '<h2 class="subheader">',
            'close': '</h2>',
        }
