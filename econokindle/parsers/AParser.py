from econokindle.Article import Article
from econokindle.TagParser import TagParser


class AParser(TagParser):

    def parse(self, item: dict) -> dict:
        attributes = item['attribs']
        target_link = attributes['href']
        # Hack to support references to articles in other issues.
        tag = {'close': '</a>'}
        referenced_article = Article()
        if self._issue.is_in_current_edition(target_link):
            tag['open'] = f'<a href="#{href}">'
        else:
            tag['open'] = f'<a href="{href}">'
            tag['close'] = ' (appendix)</a>'
        return tag
