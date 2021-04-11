from econokindle.TagParser import TagParser


class AParser(TagParser):

    def parse(self, item: dict) -> dict:
        attributes = item['attribs']
        href = self._key_creator.key(attributes['href'])
        # Hack to support references to articles in other issues.
        tag = { 'close': '</a>'}
        if href in self._valid_references:
            tag['open'] = f'<a href="#{href}">'
            return tag
        href = attributes['href']
        if href.startswith('mailto:'):
            return {'open': href, 'close': ''}
        next_child = self._peek_at_first_child(item)
        if 'data' not in next_child:
            tag['open'] = '<a>'
            return tag
        if next_child['data'] == 'article':
            tag['open'] = f'<a href="{href}">online '
        else:
            tag['open'] = f'<a href="{href}">'
            tag['close'] = ' (online)</a>'
        return tag
