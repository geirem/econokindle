from jsonpath_rw import parse

from econokindle.DocumentParser import DocumentParser


class RootParser(DocumentParser):

    def parse(self) -> dict:
        current_edition_candidates = parse('props..currentEdition..parts').find(self._script)
        if len(current_edition_candidates) == 0:
            raise Exception('Unable to find the current edition section.')
        current_edition = current_edition_candidates[0].value
        url_candidates = parse('url.canonical').find(current_edition[0])
        if len(current_edition_candidates) == 0:
            raise Exception('Unable to find the current edition URL.')
        return {
            'issue_url': url_candidates[0].value
        }
