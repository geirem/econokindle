import json
import re
from typing import Optional

from econokindle import Issue


class DocumentParser:

    def __init__(self, document: str, issue: Issue):
        self._key_creator = issue.get_key_creator()
        self._issue = issue
        self._script = self.extract_script(document)

    @staticmethod
    def extract_script(document: str) -> Optional[dict]:
        script = re.findall('<script id="preloadedData" type="application/json">.+?</script>', document.replace('\n', ''))
        script = script.pop().replace('<script id="preloadedData" type="application/json">', '')
        script = script.replace('</script>', '')
        return json.loads(script)
