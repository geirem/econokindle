import argparse
import datetime
import subprocess
from shutil import copyfile

import certifi
import urllib3
from jinja2 import Environment, FileSystemLoader

from econokindle.ArticleParser import ArticleParser
from econokindle.Cache import Cache
from econokindle.Fetcher import Fetcher
from econokindle.Issue import Issue
from econokindle.KeyCreator import KeyCreator
from econokindle.Platform import Platform

WORK = './cache/'
RESOURCES = 'resources'
env = Environment(loader=FileSystemLoader(RESOURCES))


#NOSONAR
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--edition', help='The edition to render.  Default is current edition.')
    parser.add_argument('-k', '--kindle_gen', help='Path to "kindlegen" binary.  Default is ~/bin/kindlegen')
    parser.add_argument('-f', '--cache_key', help='Force cache key.')
    return parser.parse_args()


# Node articles misbehave, as do some articles in this issue...  IDs look the same, but don't match?
def add_articles_to_appendix(fetcher: Fetcher, key_creator: KeyCreator, issue: dict, article: dict) -> None:
    for url in article['external_articles']:
        id = key_creator.key(url)
        if id in issue['references']:
            continue
        referenced_article = ArticleParser(fetcher.fetch_page(url), key_creator, issue).parse()
        if referenced_article in issue['references']:
            continue
        issue['appendix'].append(referenced_article)


#
# def process_appendix(fetcher, key_creator, issue: dict) -> None:
#     appendix_articles = issue['appendix']
#     for article_url in appendix_articles:
#         process_article(fetcher, key_creator, issue, article_url)


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


def configure_dependencies() -> list:
    args = parse_args()
    pool_manager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    if args.cache_key:
        cache_key = args.cache_key
    else:
        cache_key = str(datetime.date.today())
    key_creator = KeyCreator(cache_key)
    cache = Cache(WORK, key_creator)
    fetcher = Fetcher(pool_manager, cache)
    return [args, fetcher, key_creator]


def main():
    args, fetcher, key_creator = configure_dependencies()
    issue = Issue(fetcher, key_creator)
    issue.process_issue(args)
    render(issue)
    copyfile(RESOURCES + '/style.css', WORK + 'style.css')
    invoke_kindlegen(Platform.kindle_gen_binary(args), WORK)
    Platform.load_to_kindle(WORK, issue)


main()
