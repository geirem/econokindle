import argparse
import datetime
import re
import subprocess
from shutil import copyfile

import certifi
import urllib3
from jinja2 import Environment, FileSystemLoader

from econokindle.ArticleParser import ArticleParser
from econokindle.Cache import Cache
from econokindle.Fetcher import Fetcher
from econokindle.IndexParser import IndexParser
from econokindle.KeyCreator import KeyCreator
from econokindle.Platform import Platform
from econokindle.RootParser import RootParser

WORK = './cache/'
RESOURCES = 'resources'
file_loader = FileSystemLoader(RESOURCES)
env = Environment(loader=file_loader)


#NOSONAR
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--edition', help='The edition to render.  Default is current edition.')
    parser.add_argument('-a', '--max_age', help='Days before cached items are refreshed.  Default is five.')
    parser.add_argument('-k', '--kindle_gen', help='Path to "kindlegen" binary.  Default is ~/bin/kindlegen')
    return parser.parse_args()


def max_cache_age(args: argparse.Namespace) -> int:
    if not args.max_age:
        return 5*86400
    return int(args.max_age)


def save_cover_image(issue: dict, fetcher: Fetcher, key_creator: KeyCreator) -> None:
    url = issue['cover_image_url']
    fetcher.fetch_image(url)
    cover_image_name = key_creator.key(url)
    issue['cover_image_name'] = cover_image_name


def main():
    args = parse_args()
    pool_manager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    key_creator = KeyCreator(str(datetime.date.today()))
    cache = Cache(WORK, max_cache_age(args), key_creator)
    fetcher = Fetcher(pool_manager, cache)
    if args.edition and len(args.edition) <= 10 and re.search('^\\d{1,2}-\\d{1,2}-\\d{4}$', args.edition):
        issue_url = 'https://www.economist.com/printedition/' + args.edition
    else:
        front_url = 'https://www.economist.com/'
        print(f'Processing {front_url}...', end='')
        front = fetcher.fetch_page(front_url)
        root_parser = RootParser(front, key_creator)
        issue_url = root_parser.parse()['issue_url']
        print('done.')
    edition = issue_url.split('/').pop()
    root = fetcher.fetch_page(issue_url)
    issue = IndexParser(root, key_creator).parse()
    save_cover_image(issue, fetcher, key_creator)
    issue['title'] = 'The Economist - ' + issue['cover_title']
    for url in issue['urls']:
        print(f'Processing {url}...', end='')
        article = ArticleParser(fetcher.fetch_page(url), key_creator, issue).parse()
        for image_url in article['images']:
            fetcher.fetch_image(image_url)
        add_article_to_issue(issue, article)
        print('done.')
    add_section_links(issue)
    render(issue)
    copyfile(RESOURCES + '/style.css', WORK + 'style.css')
    invoke_kindlegen(Platform.kindle_gen_binary(args), WORK)
    Platform.load_to_kindle(WORK, edition)


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
            sections[current_name]['next_pointer'] = sections[section_names[i+1]]['id']
        i += 1


#NOSONAR
def invoke_kindlegen(kindle_gen: str, path: str) -> None:
    subprocess.call([kindle_gen, 'economist.opf'], cwd=path)


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


main()
