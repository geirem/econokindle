import argparse
import asyncio
import datetime
import os
import shutil
import sqlite3
from shutil import copyfile
import logging
import requests
from jinja2 import Environment, FileSystemLoader

from econokindle.ArticleParser import ArticleParser
from econokindle.Fetcher import Fetcher
from econokindle.IndexParser import IndexParser
from econokindle.KeyCreator import KeyCreator
from econokindle.cache.SqliteCache import SqliteCache
from econokindle.platform import load_to_kindle, convert_to_mobi
from econokindle.EmailKindle import send_mail

MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(MAIN_DIR, "work")
RESOURCES = os.path.join(MAIN_DIR, 'resources')
env = Environment(loader=FileSystemLoader(RESOURCES), autoescape=False)
_logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-k', '--kindle_gen', default='~/bin/kindle_gen',
        help='Path to "kindlegen" binary.  Defaults to ~/bin/kindlegen'
    )
    parser.add_argument(
        '-c', '--calibre', default='/Applications/calibre.app/Contents/MacOS/ebook-convert',
        help='Path to "calibre" binary.  Defaults to /Applications/calibre.app/Contents/MacOS/ebook-convert'
    )
    parser.add_argument(
        '-m', '--mobi_converter', default='system_default',
        choices=['kindlegen', 'calibre', 'system_default'],
        help='Converter application to use to convert the html file into a MOBI file. The application to use must be pre-installed on your computer.'
             ' Options are "kindlegen" which will use Amazon KindleGen, '
             '"calibre" which will use the open source Calibre application, '
             'or "system_default" which will use kindlegen when on windows, and calibre when on Mac.'
    )
    parser.add_argument(
        '-t', '--to_email', default=None, type=str,
        help='Address to send an email to when using --send_email'
    )
    parser.add_argument(
        '-f', '--from_email', default=None, type=str,
        help='Address to send an email from when using --send_email'
    )
    parser.add_argument(
        '-p', '--password_email', default=None, type=str,
        help='Password (app specific password) to send an email with.'
    )

    parser.add_argument(
        '-s', '--send_email', default=False, type=bool,
        help='If true, will try to email the economist edition to the given to email address, using the from address.'
    )

    return parser.parse_args()


def setup_logger(logger):
    logger.setLevel(logging.INFO)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    fh = logging.FileHandler(os.path.join(WORK, "econologger.log"))
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


async def process_issue(fetcher: Fetcher, key_creator: KeyCreator, args: argparse.Namespace) -> None:
    setup_logger(_logger)
    _logger.info("processing issue")
    issue_url = 'https://www.economist.com/printedition'
    print(f'Processing {issue_url}...', end='')
    issue = IndexParser(fetcher.fetch_page(issue_url), key_creator).parse()
    cover_image = fetcher.fetch_image(issue['cover_image_url'])
    with open(os.path.join(WORK, "cover.jpg"), 'wb') as out:
        out.write(cover_image)
    print('done.')
    _logger.info("processing articles")
    await process_articles_in_issue(fetcher, key_creator, issue)
    add_section_links(issue)
    render(issue)
    copyfile(os.path.join(RESOURCES, 'style.css'), os.path.join(WORK, 'style.css'))
    _logger.info("converting to mobi")
    convert_to_mobi(args, WORK)
    load_to_kindle(WORK, issue)
    if args.send_email:
        _logger.info("sending email")
        send_mail(args.from_email, args.password_email, [args.to_email],
                  "economist weekly edition", "heres the weekly edition",
                  files=[os.path.join(WORK, issue['edition'] + '_economist.mobi')])
    _logger.info("done")

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
        with open(os.path.join(WORK, key_creator.key(image_url).lower()), 'wb') as out:
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
    with open(os.path.join(WORK, file), 'wt') as writer:
        writer.write(content)


def configure_dependencies() -> list:
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    args = parse_args()
    key_creator = KeyCreator(str(datetime.date.today()))
    conn = sqlite3.connect('cache.db')
    cache = SqliteCache(conn, key_creator)
    session = requests.session()
    fetcher = Fetcher(session, cache)
    return [args, fetcher, key_creator]


async def main():
    args, fetcher, key_creator = configure_dependencies()
    await process_issue(fetcher, key_creator, args)


if __name__ == "__main__":
    asyncio.run(main())
