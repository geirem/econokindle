from jsonpath_rw import parse

from econokindle.DocumentParser import DocumentParser


class IndexParser(DocumentParser):

    def parse(self) -> None:
        name = ''
        cover = parse('$..cover').find(self._script).pop().value.pop()
        canonical = parse('[*].response.canonical').find(self._script).pop().value
        for item in canonical:
            if item.startswith('_hasPart'):
                name = item
                break
        if name == '':
            raise Exception
        self._issue.set_cover_url(cover['url']['canonical'])
        self._issue.set_cover_title(cover['headline'])
        self._issue.set_edition(canonical['url']['canonical'].split('/').pop())
        parts = canonical[name]['parts']
        for part in parts:
            self._issue.add_article_reference(part['url']['canonical'])
