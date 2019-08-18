from lib import KeyCreator
from lib.TagParser import TagParser


class AParser(TagParser):
    #
    # def __init__(self, key_creator: KeyCreator, images: list, valid_references: list):
    #     super().__init__(key_creator, images, valid_references)

    def parse(self, tag: dict) -> dict:
        attributes = tag['attribs']
        href = self._key_creator.key(attributes['href'])
        # Hack to support references to articles in other issues.
        tag = { 'close': '</a>'}
        if href in self._valid_references:
            tag['open'] = f'<a href="#{href}">'
        else:
            href = attributes['href']
            tag['open'] = f'<a href="{href}">online '
        return tag
