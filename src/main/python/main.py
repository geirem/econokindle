import json
import re
from typing import Optional
from shutil import copyfile
import subprocess

import urllib3
import certifi

from lib.Cache import Cache
from lib.Fetcher import Fetcher
from jinja2 import Environment, FileSystemLoader

from lib.parsers.Parser import Parser
from lib.parsers.CanonicalParser import CanonicalParser
from lib.parsers.CartoonParser import CartoonParser
from lib.parsers.ContentParser import ContentParser
from lib.parsers.NullParser import NullParser
from collections import OrderedDict

WORK = './cache/'
RESOURCES = 'src/main/resources'
KINDLE_GEN = '/Users/geirem/bin/kindlegen'
pool_manager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
cache = Cache(WORK)
fetcher = Fetcher(pool_manager, cache)
file_loader = FileSystemLoader(RESOURCES)
env = Environment(loader=file_loader)
re.DOTALL = True


ARTICLE_FILTER = [
    'politics-this-week',
    'business-this-week',
    'economic-data-commodities-and-markets',
]


def parse_root(document: str) -> list:
    jscript = extract_script(document)
    urls = jscript[1]['response']['canonical']['_hasPart3HyMUO']['parts']
    return urls


def extract_script(document: str) -> Optional[dict]:
    script = re.findall('<script id="preloadedData" type="application/json">.+?</script>', document.replace('\n', ''))
    script = script.pop().replace('<script id="preloadedData" type="application/json">', '')
    script = script.replace('</script>', '')
    try:
        return json.loads(script)
    except:
        return None


def article_filter(url: str) -> bool:
    if url.split('/').pop() in ARTICLE_FILTER:
        return False
    if url.split('/')[3] in ['letters', 'graphic-detail']:
        return False
    return True


def main():
    edition = '2019-08-03'
    root = fetcher.fetch('https://www.economist.com/printedition/' + edition)
    raw_articles = parse_root(root)
    images = []
    sections = OrderedDict()
    sections['HIDDEN'] = []
    sections['Leaders'] = []
    for article in raw_articles:
        url = article['url']['canonical']
        if not article_filter(url):
            continue
        document = fetcher.fetch(url)
        script = extract_script(document)
        if script is None:
            print('No script: ' + url)
            continue
        parser = parsing_strategy(script, images, url)
        content = parser.parse()
        if content == {} or content is None:
            print('Script not parsable: ' + url)
            print(parser)
            continue
        section = content['section']
        if section == 'The world this week' or section == 'Economic and financial indicators':
            continue
        if section not in sections:
            sections[section] = []
        sections[section].append(content)
    for image in images:
        fetcher.fetch_image(image)
    render('toc.jinja', 'toc.html', sections, 'The Economist ' + edition)
    render('ncx.jinja', 'toc.ncx', sections, 'The Economist ' + edition)
    render('book.jinja', 'economist.html', sections, 'The Economist ' + edition)
    render('opf.jinja', 'economist.opf', sections, 'The Economist ' + edition)
    copyfile(RESOURCES + '/style.css', WORK + 'style.css')
    subprocess.call([KINDLE_GEN, 'economist.opf'], cwd=WORK)
    copyfile(WORK + 'economist.mobi', 'economist.mobi')


def render(template: str, file: str, sections: OrderedDict, title: str) -> None:
    content = env.get_template(template).render(sections=sections, title=title)
    with open(WORK + file, 'wt') as writer:
        writer.write(content)


def parsing_strategy(script: dict, images: list, url: str) -> Parser:
    if url.endswith('kals-cartoon'):
        return CartoonParser(CartoonParser.wants(script), images)
    content = CanonicalParser.wants(script)
    if content:
        return CanonicalParser(content, images)
    content = ContentParser.wants(script)
    if content:
        return ContentParser(content, images)
    return NullParser(script, images)


main()
