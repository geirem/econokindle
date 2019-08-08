import json
import re
import subprocess
from collections import OrderedDict
from shutil import copyfile
from typing import Optional

import certifi
import urllib3
from jinja2 import Environment, FileSystemLoader

from lib.Cache import Cache
from lib.Fetcher import Fetcher
from lib.parsers.CanonicalParser import CanonicalParser
from lib.parsers.CartoonParser import CartoonParser
from lib.parsers.Parser import Parser

WORK = './cache/'
RESOURCES = 'src/main/resources'
KINDLE_GEN = '/Users/geirem/bin/kindlegen'
pool_manager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
cache = Cache(WORK)
fetcher = Fetcher(pool_manager, cache)
file_loader = FileSystemLoader(RESOURCES)
env = Environment(loader=file_loader)


def extract_script(document: str) -> Optional[dict]:
    script = re.findall('<script id="preloadedData" type="application/json">.+?</script>', document.replace('\n', ''))
    script = script.pop().replace('<script id="preloadedData" type="application/json">', '')
    script = script.replace('</script>', '')
    return json.loads(script)


def article_filter(url: str) -> bool:
    if url.split('/').pop() in [
        'politics-this-week',
        'business-this-week',
        'economic-data-commodities-and-markets',
    ]:
        return False
    if url.split('/')[3] in ['letters', 'graphic-detail']:
        return False
    return True


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
        if not article_filter(url):
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


def save_cover_image(issue: dict) -> None:
    url = issue['cover_image_url']
    fetcher.fetch_image(url)
    cover_image_name = url.split('/').pop()
    issue['cover_image_name'] = cover_image_name


def main():
    edition = '2019-08-03'
    root = fetcher.fetch('https://www.economist.com/printedition/' + edition)
    issue = parse_root(root)
    save_cover_image(issue)
    issue['title'] = 'The Economist - ' + edition
    images = []
    sections = issue['sections']
    article_count = 0
    for url in issue['urls']:
        document = fetcher.fetch(url)
        script = extract_script(document)
        parser = parsing_strategy(script, images, url)
        article = parser.parse()
        section = article['section']
        article_count += 1
        article['id'] = 'article_' + str(article_count)
        sections[section]['articles'].append(article)
    for image in images:
        fetcher.fetch_image(image)
    render('toc.jinja', 'toc.html', issue)
    render('ncx.jinja', 'toc.ncx', issue)
    render('book.jinja', 'economist.html', issue)
    render('opf.jinja', 'economist.opf', issue)
    copyfile(RESOURCES + '/style.css', WORK + 'style.css')
    subprocess.call([KINDLE_GEN, 'economist.opf'], cwd=WORK)
    copyfile(WORK + 'economist.mobi', 'economist.mobi')


def render(template: str, file: str, issue: dict) -> None:
    sections = issue['sections']
    content = env.get_template(template).render(sections=sections, title=issue['title'], issue=issue)
    with open(WORK + file, 'wt') as writer:
        writer.write(content)


def parsing_strategy(script: dict, images: list, url: str) -> Parser:
    if url.endswith('kals-cartoon'):
        return CartoonParser(CartoonParser.wants(script), images)
    content = CanonicalParser.wants(script)
    return CanonicalParser(content, images)


main()
