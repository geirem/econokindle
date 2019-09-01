import json
import re
from typing import Optional

from econokindle import KeyCreator


class DocumentParser:

    def __init__(self, document: str, key_creator: KeyCreator):
        self._key_creator = key_creator
        self._script = self.extract_script(document)

    @staticmethod
    def extract_script(document: str) -> Optional[dict]:
        script = re.findall('<script id="preloadedData" type="application/json">.+?</script>', document.replace('\n', ''))
        script = script.pop().replace('<script id="preloadedData" type="application/json">', '')
        script = script.replace('</script>', '')
        return json.loads(script)
