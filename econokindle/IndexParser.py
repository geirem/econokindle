from collections import OrderedDict

from econokindle.DocumentParser import DocumentParser
from jsonpath_rw import parse


class IndexParser(DocumentParser):

    def parse(self) -> dict:
        name = ''
        cover = parse('$..cover').find(self._script).pop().value.pop()
        canonical = parse('[*].response.canonical').find(self._script).pop().value
        for item in canonical:
            if item.startswith('_hasPart'):
                name = item
                break
        if name == '':
            raise Exception
        cover_url = cover['url']['canonical']
        cover_title = cover['headline']
        self_url = canonical['url']['canonical']
        edition = self_url.split('/').pop()
        parts = canonical[name]['parts']
        urls = []
        references = []
        sections = OrderedDict()
        for part in parts:
            url = part['url']['canonical']
            urls.append(url)
            references.append(self._key_creator.key(url))
        return {
            'cover_image_url': cover_url,
            'cover_title': cover_title,
            'sections': sections,
            'urls': urls,
            'references': references,
            'cover_image_name': self._key_creator.key(cover_url),
            'edition': edition,
            'title': 'The Economist - ' + cover_title,
        }

