import argparse
import json
import os
import platform
import re
import subprocess
from collections import OrderedDict
from shutil import copyfile
from typing import Optional

import certifi
import urllib3
from jinja2 import Environment, FileSystemLoader
from jsonpath_rw import parse

from lib.Cache import Cache
from lib.Fetcher import Fetcher
from lib.KeyCreator import KeyCreator
from lib.Parser import Parser
from lib.ParsingStrategy import ParsingStrategy
from lib.Platform import Platform

WORK = './cache/'
RESOURCES = 'src/main/resources'
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


def extract_script(document: str) -> Optional[dict]:
    script = re.findall('<script id="preloadedData" type="application/json">.+?</script>', document.replace('\n', ''))
    script = script.pop().replace('<script id="preloadedData" type="application/json">', '')
    script = script.replace('</script>', '')
    return json.loads(script)


def parse_root(document: str, key_creator: KeyCreator) -> dict:
    jscript = extract_script(document)
    name = ''
    cover = parse('$..cover').find(jscript).pop().value.pop()
    canonical = parse('[*].response.canonical').find(jscript).pop().value
    for item in canonical:
        if item.startswith('_hasPart'):
            name = item
            break
    if name == '':
        raise Exception
    cover_url = cover['url']['canonical']
    cover_title = cover['headline']
    parts = canonical[name]['parts']
    urls = []
    references = []
    sections = OrderedDict()
    for part in parts:
        url = part['url']['canonical']
        urls.append(url)
        references.append(key_creator.key(url))
    return {
        'cover_image_url': cover_url,
        'cover_title': cover_title,
        'sections': sections,
        'urls': urls,
        'references': references,
    }


def save_cover_image(issue: dict, fetcher: Fetcher, key_creator: KeyCreator) -> None:
    url = issue['cover_image_url']
    fetcher.fetch_image(url)
    cover_image_name = key_creator.key(url)
    issue['cover_image_name'] = cover_image_name


def parse_index(script: dict) -> str:
    for item in script:
        if 'canonical' not in item['response']:
            continue
        for sub_item, value in item['response']['canonical'].items():
            if sub_item.startswith('_hasPart'):
                return value['parts'][0]['url']['canonical']


def main():
    args = parse_args()
    pool_manager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    key_creator = KeyCreator()
    cache = Cache(WORK, max_cache_age(args), key_creator)
    fetcher = Fetcher(pool_manager, cache)
    if args.edition and len(args.edition) <= 10 and re.search('^\\d{1,2}-\\d{1,2}-\\d{4}$', args.edition):
        issue_pointer = 'https://www.economist.com/printedition/' + args.edition
    else:
        front = fetcher.fetch('https://www.economist.com/')
        front_script = extract_script(front)
        issue_pointer = parse_index(front_script)
    root = fetcher.fetch(issue_pointer)
    issue = parse_root(root, key_creator)
    save_cover_image(issue, fetcher, key_creator)
    issue['title'] = 'The Economist - ' + issue['cover_title']
    sections = issue['sections']
    for url in issue['urls']:
        print(f'Processing {url}...', end='')
        document = fetcher.fetch(url)
        article = Parser(extract_script(document), key_creator, issue).parse()
        for image_url in article['images']:
            fetcher.fetch_image(image_url)
        section = article['section']
        if section not in sections:
            sections[section] = {
                'articles': [],
                'id': 'section_' + str(len(sections)),
            }
        sections[section]['articles'].append(article)
        print('done.')
    render(issue)
    copyfile(RESOURCES + '/style.css', WORK + 'style.css')
    invoke_kindlegen(Platform.kindle_gen_binary(args), WORK)
    Platform.load_to_kindle(WORK)


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
