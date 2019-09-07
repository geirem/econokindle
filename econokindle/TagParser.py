from typing import Optional

from econokindle import Article, Issue


class TagParser:

    _supports = '*'

    def __init__(self, issue: Issue, article: Article):
        self._issue = issue
        self._article = article

    def parse(self, tag: dict) -> dict:
        name = tag['name']
        return {
            'open': f'<{name}>',
            'close': f'</{name}>',
        }

    @staticmethod
    def _peek_at_first_child(tag: dict) -> Optional[dict]:
        if 'children' not in tag:
            return None
        children = tag['children']
        if len(children) == 0:
            return None
        return children[0]

    def supports(self):
        return self._supports
