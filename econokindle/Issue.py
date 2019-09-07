import argparse
from collections import OrderedDict
import re

from econokindle import Fetcher
from econokindle.Article import Article
from econokindle.ArticleParser import ArticleParser
from econokindle.IndexParser import IndexParser
from econokindle.KeyCreator import KeyCreator
from deprecated import deprecated

from econokindle.RootParser import RootParser


class Issue:

    def __init__(self, fetcher: Fetcher, key_creator: KeyCreator):
        self.__fetcher = fetcher
        self.__key_creator = key_creator
        self.__structure = {
            'sections': OrderedDict(),
            'urls': [],
            'references': [],
            'appendix': [],
            'title': ''
        }
        self.__known_urls = []

    def set_cover_url(self, url: str) -> None:
        self.__structure['cover_image_name'] = self.__key_creator.key(url)
        self.__structure['cover_image_url'] = url
        if url not in self.__known_urls:
            self.__fetcher.fetch_image(url)
            self.__known_urls.append(url)

    def get_cover_url(self) -> str:
        return self.__structure['cover_image_url']

    def set_cover_title(self, cover_title: str) -> None:
        self.__structure['cover_title'] = cover_title
        self.__structure['title'] = 'The Economist - ' + cover_title

    def set_edition(self, edition: str) -> None:
        self.__structure['edition'] = edition

    def get_references(self) -> list:
        return self.__structure['references']

    def add_article_reference(self, url: str) -> None:
        self.__structure['url'].append(url)
        self.__structure['references'].append(self.__key_creator.key(url))
        if url not in self.__known_urls:
            self.__fetcher.fetch_image(url)
            self.__known_urls.append(url)

    def __add_section_links(self) -> None:
        sections = self.__structure['sections']
        section_names = list(sections.keys())
        i = 0
        last_index = len(section_names)
        while i < last_index:
            current_name = section_names[i]
            if i < last_index - 1:
                sections[current_name]['next_pointer'] = sections[section_names[i+1]]['id']
            i += 1

    @deprecated
    def get_key_creator(self) -> KeyCreator:
        return self.__key_creator

    def __find_issue_url(self, **kwargs: dict) -> str:
        front_url = 'https://www.economist.com/'
        if 'edition' in kwargs and kwargs['edition']:
            edition = str(kwargs['edition'])
            if re.search('^\\d{4}-\\d{2}-\\d{2}$', edition):
                return front_url + 'printedition/' + edition
            else:
                raise SyntaxError('Invalid edition date format.')
        print(f'Processing {front_url}...', end='')
        issue_url = RootParser(self.__fetcher.fetch_page(front_url), self).parse()['issue_url']
        print('done.')
        return issue_url

    def process_issue(self, args: argparse.Namespace) -> None:
        issue_url = self.__find_issue_url(edition=args.edition)
        print(f'Processing {issue_url}...', end='')
        IndexParser(self.__fetcher.fetch_page(issue_url), self).parse()
        print('done.')
        self.__process_articles()
        self.__add_section_links()
        # process_appendix(fetcher, key_creator, issue)

    def __process_articles(self) -> None:
        for url in self.__structure['urls']:
            print(f'Processing {url}...', end='')
            article = Article(self.__fetcher, self.__key_creator)
            ArticleParser(self.__fetcher.fetch_page(url), article, self).parse()
            self.__fetcher.fetch_images(article['images'])
            # self.__add_article_to_issue(article)
            # add_articles_to_appendix(fetcher, key_creator, issue, article)
            print('done.')

    def add_article_to_section(self, section: str, article: Article) -> None:
        sections = self.__structure['sections']
        # section = article['section']
        if section not in sections:
            sections[section] = {
                'articles': [],
                'id': 'section_' + str(len(sections)),
            }
        sections[section]['articles'].append(article)
