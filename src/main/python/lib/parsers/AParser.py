from lib import KeyCreator
from lib.TagParser import TagParser


class AParser(TagParser):

    def parse(self, item: dict) -> dict:
        attributes = item['attribs']
        href = self._key_creator.key(attributes['href'])
        # Hack to support references to articles in other issues.
        tag = { 'close': '</a>'}
        if href in self._valid_references:
            tag['open'] = f'<a href="#{href}">'
        else:
            href = attributes['href']
            next_child = self._peek_at_first_child(item)
            if next_child['data'] == 'article':
                tag['open'] = f'<a href="{href}">online '
            else:
                tag['open'] = f'<a href="{href}">'
                tag['close'] = ' (online)</a>'
        return tag
