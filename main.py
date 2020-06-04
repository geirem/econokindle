import argparse
import asyncio
import datetime
import os
import shutil
import sqlite3
from shutil import copyfile

import certifi
import urllib3
from jinja2 import Environment, FileSystemLoader

from econokindle.ArticleParser import ArticleParser
from econokindle.Fetcher import Fetcher
from econokindle.IndexParser import IndexParser
from econokindle.KeyCreator import KeyCreator
from econokindle.platform import load_to_kindle, convert_to_mobi
from econokindle.cache.SqliteCache import SqliteCache

WORK = './work/'
RESOURCES = 'resources'
env = Environment(loader=FileSystemLoader(RESOURCES), autoescape=False)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--kindle_gen', help='Path to "kindlegen" binary.  Defaults to ~/bin/kindlegen')
    parser.add_argument(
        '-c', '--calibre',
        help='Path to "calibre" binary.  Defaults to /Applications/calibre.app/Contents/MacOS/ebook-convert'
    )
    return parser.parse_args()


async def process_issue(fetcher: Fetcher, key_creator: KeyCreator, args: argparse.Namespace) -> None:
    issue_url = 'https://www.economist.com/printedition'
    print(f'Processing {issue_url}...', end='')
    issue = IndexParser(fetcher.fetch_page(issue_url), key_creator).parse()
    cover_image = fetcher.fetch_image(issue['cover_image_url'])
    with open(WORK + key_creator.key(issue['cover_image_url']), 'wb') as out:
        out.write(cover_image)
    print('done.')
    await process_articles_in_issue(fetcher, key_creator, issue)
    add_section_links(issue)
    render(issue)
    copyfile(RESOURCES + '/style.css', WORK + 'style.css')
    convert_to_mobi(args, WORK)
    load_to_kindle(WORK, issue)


async def process_articles_in_issue(fetcher: Fetcher, key_creator: KeyCreator, issue: dict) -> None:
    for url in issue['urls']:
        print(f'Processing {url}...', end='')
        if url.endswith(issue['edition']):
            print('special content index, skipping.')
            continue
        article_content = fetcher.fetch_page(url)
        article = await process_article_content(article_content, issue, key_creator)
        fetch_article_images(article, fetcher, key_creator)
        add_article_to_issue(issue, article)
        print('done.')


async def process_article_content(article_content, issue, key_creator):
    return ArticleParser(article_content, key_creator, issue).parse()


def fetch_article_images(article, fetcher, key_creator):
    for image_url in article['images']:
        image = fetcher.fetch_image(image_url)
        with open(WORK + key_creator.key(image_url).lower(), 'wb') as out:
            out.write(image)


def add_article_to_issue(issue: dict, article: dict) -> None:
    sections = issue['sections']
    section = article['section']
    if section not in sections:
        sections[section] = {
            'articles': [],
            'id': 'section_' + str(len(sections)),
        }
    sections[section]['articles'].append(article)


def add_section_links(issue: dict) -> None:
    sections = issue['sections']
    section_names = list(sections.keys())
    i = 0
    last_index = len(section_names)
    while i < last_index:
        current_name = section_names[i]
        if i < last_index - 1:
            sections[current_name]['next_pointer'] = sections[section_names[i + 1]]['id']
        i += 1


def render(issue: dict) -> None:
    render_template('toc.jinja', 'toc.html', issue)
    render_template('ncx.jinja', 'toc.ncx', issue)
    render_template('book.jinja', 'economist.html', issue)
    render_template('opf.jinja', 'economist.opf', issue)


def render_template(template: str, file: str, issue: dict) -> None:
    sections = issue['sections']
    content = env.get_template(template).render(sections=sections, title=issue['title'], issue=issue)
    with open(WORK + file, 'wt') as writer:
        writer.write(content)


def configure_dependencies() -> list:
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    args = parse_args()
    pool_manager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    key_creator = KeyCreator(str(datetime.date.today()))
    conn = sqlite3.connect('cache.db')
    cache = SqliteCache(conn, key_creator)
    fetcher = Fetcher(pool_manager, key_creator, cache)
    return [args, fetcher, key_creator]


async def main():
    args, fetcher, key_creator = configure_dependencies()
    await process_issue(fetcher, key_creator, args)


if __name__ == "__main__":
    asyncio.run(main())
