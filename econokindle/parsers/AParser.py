from econokindle.TagParser import TagParser


class AParser(TagParser):

    def parse(self, item: dict) -> dict:
        attributes = item['attribs']
        href = self._key_creator.key(attributes['href'])
        # Hack to support references to articles in other issues.
        tag = { 'close': '</a>'}
        if href in self._valid_references:
            tag['open'] = f'<a href="#{href}">'
        else:
            self._external_articles.append(attributes['href'])
            next_child = self._peek_at_first_child(item)
            if next_child['data'] == 'article':
                tag['open'] = f'<a href="{href}">appendix '
            else:
                tag['open'] = f'<a href="{href}">'
                tag['close'] = ' (appendix)</a>'
        return tag
