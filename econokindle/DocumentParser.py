import json
from typing import Optional

from bs4 import BeautifulSoup

from econokindle import KeyCreator


class DocumentParser:

    def __init__(self, document: str, key_creator: KeyCreator):
        self._key_creator = key_creator
        self._script = self.extract_script(document)

    @staticmethod
    def extract_script(document: str) -> Optional[dict]:
        bs = BeautifulSoup(document, 'html.parser')
        results = bs.find('script', {'id': '__NEXT_DATA__'})
        return json.loads(results.contents.pop())

    @staticmethod
    def _apply_html_entities(processed: Optional[str]) -> str:
        if processed is None:
            return ''
        return processed.encode(encoding='ascii', errors='xmlcharrefreplace').decode('utf-8')
