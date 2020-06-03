from collections import OrderedDict

from econokindle.DocumentParser import DocumentParser
from jsonpath_rw import parse


class IndexParser(DocumentParser):

    def parse(self) -> dict:
        cover = parse('$..cover').find(self._script).pop().value.pop()
        parts = parse('props.pageProps.content.hasPart.parts').find(self._script).pop().value
        self_url = parse('props.pageProps.pageUrl').find(self._script).pop().value
        cover_title = parse('props.pageProps.content.headline').find(self._script).pop().value
        cover_url = cover['url']['canonical']
        edition = self_url.split('/').pop()
        urls = []
        references = []
        sections = OrderedDict()
        for part in parts:
            url = part['url']['canonical']
            urls.append(url)
            references.append(self._key_creator.key(url))
        return {
            'cover_image_url': cover_url,
            'cover_title': self._apply_html_entities(cover_title),
            'sections': sections,
            'urls': urls,
            'references': references,
            'cover_image_name': self._key_creator.key(cover_url),
            'edition': edition,
            'title': self._apply_html_entities('The Economist - ' + cover_title),
        }

