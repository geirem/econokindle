from econokindle import Fetcher, KeyCreator


class Article:

    def __init__(self, fetcher: Fetcher, key_creator: KeyCreator):
        self.__fetcher = fetcher
        self.__key_creator = key_creator
        self.__structure = {}

    def set_url(self, url: str) -> None:
        self.__structure['id'] = self.__key_creator.key(url)

    def set_image(self, url: str) -> None:
        self.__structure['image'] = self.__key_creator.key(url)
        self.__fetcher.fetch_image(url)

    def set_title(self, title: str) -> None:
        self.__structure['title'] = title

    def set_text(self, text: str) -> None:
        self.__structure['text'] = text

    def set_subheadline(self, subheadline: str) -> None:
        self.__structure['subheadline'] = subheadline

    def set_description(self, description: str) -> None:
        self.__structure['description'] = description

    def setdateline(self, dateline: str) -> None:
        self.__structure['dateline'] = dateline

#         result = {
#             'title': self.__apply_html_entities(self.__script['headline']),
#             'text': self.__apply_html_entities(''.join(self.__parsed_elements)),
#             'section': self.__apply_html_entities(self.__script['print']['section']['headline']),
#             'subheadline': self.__apply_html_entities(self.__script['subheadline']),
#             'description': self.__apply_html_entities(self.__script['description']),
#             'dateline': self.__apply_html_entities(self.__script['dateline']),
#             'image': image,
#             'images': self.__images,
#             'external_articles': self.__parsing_strategy.get_external_articles(),
#         }
