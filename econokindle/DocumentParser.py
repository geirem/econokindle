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
        results = BeautifulSoup(document, 'html.parser').select('#preloadedData')
        return json.loads(results.pop().contents.pop())
