from econokindle.DocumentParser import DocumentParser


class RootParser(DocumentParser):

    def parse(self) -> dict:
        for item in self._script:
            if 'canonical' not in item['response']:
                continue
            for sub_item, value in item['response']['canonical'].items():
                if sub_item.startswith('_hasPart'):
                    return {
                        'issue_url': value['parts'][0]['url']['canonical']
                    }
