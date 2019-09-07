from typing import Optional

from jsonpath_rw import parse

from econokindle import KeyCreator, Issue, Article
from econokindle.DocumentParser import DocumentParser
from econokindle.ParsingStrategy import ParsingStrategy


class ArticleParser(DocumentParser):

    def __init__(self, document: str, article: Article, issue: Issue):
        super().__init__(document, issue)
        candidates = parse('[*].response.canonical').find(self._script)
        for candidate in candidates:
            if 'url' in candidate.value:
                self.__script = candidate.value
                break
        self.__images = []
        self.__parsed_elements = []
        self.__url_path = parse('image.main.url.canonical')
        self.__article = article
        self.__issue = issue
        self.__parsing_strategy = ParsingStrategy(issue, article)

    def __extract_main_image(self) -> Optional[str]:
        url = self.__url_path.find(self.__script)
        if len(url) == 1:
            return url.pop().value
        return None

    def __find_text_data(self) -> dict:
        for item in self.__script:
            if item.startswith('_text'):
                return self.__script[item]

    def __start_body_parsing(self) -> None:
        for item in self.__script:
            if item.startswith('_text'):
                self.__parse_article_body(self.__script[item])
                return

    def parse(self) -> None:
        self.__article.set_url(self.__script['url']['canonical'])
        image = self.__extract_main_image()
        self.__start_body_parsing()
        if image:
            self.__article.set_image()
        self.__article.set_title(self.__apply_html_entities(self.__script['headline']))
        self.__article.set_text(self.__apply_html_entities(''.join(self.__parsed_elements)))
        self.__article.set_subheadline(self.__apply_html_entities(self.__script['subheadline']))
        self.__article.set_description(self.__apply_html_entities(self.__script['description']))
        self.__article.set_dateline(self.__apply_html_entities(self.__script['dateline']))
        self.__issue.add_article_to_section(self.__apply_html_entities(self.__script['print']['section']['headline']), self.__article)
        # result = {
            # 'image': image,
            # 'images': self.__images,
            # 'external_articles': self.__parsing_strategy.get_external_articles(),
        # }

    def __parse_article_body(self, element: dict) -> None:
        for item in element:
            if item['type'] == 'text':
                self.__parsed_elements.append(item['data'])
            elif item['type'] == 'tag':
                tag = self.__parsing_strategy.get_parser(item).parse(item)
                self.__parsed_elements.append(tag['open'])
                self.__parse_article_body(item['children'])
                self.__parsed_elements.append(tag['close'])

    @staticmethod
    def __apply_html_entities(processed: Optional[str]) -> str:
        if processed is None:
            return ''
        return processed.encode(encoding='ascii', errors='xmlcharrefreplace').decode('utf-8')
