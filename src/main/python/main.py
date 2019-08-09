import json
import os
import re
import subprocess
from collections import OrderedDict
from shutil import copyfile
from typing import Optional
import argparse
import certifi
import urllib3
from jinja2 import Environment, FileSystemLoader

from lib.Cache import Cache
from lib.Fetcher import Fetcher
from lib.Parser import Parser

WORK = './cache/'
RESOURCES = 'src/main/resources'
file_loader = FileSystemLoader(RESOURCES)
env = Environment(loader=file_loader)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--edition', help='The edition to render.  Default is current edition.')
    parser.add_argument('-a', '--max_age', help='Days before cached items are refreshed.  Default is five.')
    parser.add_argument('-k', '--kindlegen', help='Path to "kindlegen" binary.  Default is ~/bin/kindlegen')
    return parser.parse_args()


def extract_script(document: str) -> Optional[dict]:
    script = re.findall('<script id="preloadedData" type="application/json">.+?</script>', document.replace('\n', ''))
    script = script.pop().replace('<script id="preloadedData" type="application/json">', '')
    script = script.replace('</script>', '')
    return json.loads(script)


def should_exclude_article(url: str) -> bool:
    if url.split('/').pop() in [
        'politics-this-week',
        'business-this-week',
        'economic-data-commodities-and-markets',
    ]:
        return True
    if url.split('/')[3] in [
        'letters',
        'graphic-detail'
    ]:
        return True
    return False


def parse_root(document: str) -> dict:
    jscript = extract_script(document)
    name = ''
    for item in jscript[1]['response']['canonical']:
        if item.startswith('_hasPart'):
            name = item
            break
    if name == '':
        raise Exception
    canonical = jscript[1]['response']['canonical']
    cover = canonical['image']['cover'][0]
    cover_url = cover['url']['canonical']
    cover_title = cover['headline']
    parts = canonical[name]['parts']
    urls = []
    sections = OrderedDict()
    for part in parts:
        url = part['url']['canonical']
        if should_exclude_article(url):
            continue
        urls.append(url)
        section = part['print']['section']['headline']
        if section not in sections:
            sections[section] = {
                'articles': [],
                'id': 'section_' + str(len(sections)),
            }
    return {
        'cover_image_url': cover_url,
        'cover_title': cover_title,
        'sections': sections,
        'urls': urls,
    }


def save_cover_image(issue: dict, fetcher: Fetcher) -> None:
    url = issue['cover_image_url']
    fetcher.fetch_image(url)
    cover_image_name = url.split('/').pop()
    issue['cover_image_name'] = cover_image_name


def main():
    args = parse_args()
    pool_manager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    cache = Cache(WORK, args.max_age*86400 if args.max_age else 5*86400)
    edition = args.edition if args.edition else '2019-08-10'
    kindle_gen = args.kindle_gen if args.kindle_gen else os.environ['HOME'] + '/bin/kindlegen'
    fetcher = Fetcher(pool_manager, cache)
    root = fetcher.fetch('https://www.economist.com/printedition/' + edition)
    issue = parse_root(root)
    save_cover_image(issue, fetcher)
    issue['title'] = 'The Economist - ' + edition
    sections = issue['sections']
    article_count = 0
    for url in issue['urls']:
        document = fetcher.fetch(url)
        script = extract_script(document)
        parser = Parser(script)
        article = parser.parse()
        for image_url in article['images']:
            fetcher.fetch_image(image_url)
        section = article['section']
        article_count += 1
        article['id'] = 'article_' + str(article_count)
        sections[section]['articles'].append(article)
    render('toc.jinja', 'toc.html', issue)
    render('ncx.jinja', 'toc.ncx', issue)
    render('book.jinja', 'economist.html', issue)
    render('opf.jinja', 'economist.opf', issue)
    copyfile(RESOURCES + '/style.css', WORK + 'style.css')
    subprocess.call([kindle_gen, 'economist.opf'], cwd=WORK)
    copyfile(WORK + 'economist.mobi', 'economist.mobi')


def render(template: str, file: str, issue: dict) -> None:
    sections = issue['sections']
    content = env.get_template(template).render(sections=sections, title=issue['title'], issue=issue)
    with open(WORK + file, 'wt') as writer:
        writer.write(content)


main()
