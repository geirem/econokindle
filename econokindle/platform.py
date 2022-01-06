import argparse
import os
import platform
import subprocess
from shutil import copyfile
from typing import Optional, List

ConversionCommand = Optional[List[str]]


def load_to_kindle(work: str, issue: dict) -> None:
    cached_name = work + 'economist.mobi'
    cached_edition_name = work + issue['edition'] + '_economist.mobi'
    root = 'D:/documents/' if _is_windows() else '/Volumes/Kindle/documents/'
    target_name = root + issue['edition'] + '_economist.mobi'
    os.rename(cached_name, cached_edition_name)
    print("File renamed to: " + cached_edition_name)
    if os.path.isdir(root):
        copyfile(cached_edition_name, target_name)


def _is_windows() -> bool:
    return platform.system() == 'Windows'


def convert_to_mobi(args: argparse.Namespace, path: str) -> None:
    """ Assumes that kindlegen is used on Windows, and Calibre on MacOS.  This
        whole converter selection is a bit smelly, and should probably be heavily
        refactored.   Some other day. """
    processor = None
    if str(args.mobi_converter) == "system_default":
        processor = _kindlegen(args) if _is_windows() else _calibre(args)
    elif str(args.mobi_converter) == "calibre":
        processor = _calibre(args)
    elif str(args.mobi_converter) == "kindlegen":
        processor = _kindlegen(args)
    if processor is None:
        raise Exception('No conversion binary found, unable to render MOBI.')
    completed_process = subprocess.run(processor, cwd=path)
    conversion_exception_str = "Conversion from html/opf file to mobi file failed. Do you have a converter app" \
                               " like Calibre or KindleGen installed as per the README?"
    if completed_process.returncode != 0:
        raise Exception(conversion_exception_str)
    if not os.path.isfile(os.path.join(path, 'economist.mobi')):
        raise Exception("Output file not found. " + conversion_exception_str)


def _calibre(args: argparse.Namespace) -> ConversionCommand:
    binary = '/Applications/calibre.app/Contents/MacOS/ebook-convert'
    if args.calibre:
        binary = str(args.calibre)
        if not os.path.isfile(binary) and not binary.endswith('/ebook-convert'):
            return None
    return [
        binary, 'economist.html', 'economist.mobi',
        '--max-toc-links=250', '--page-breaks-before=/', '--verbose', '--disable-markup-chapter-headings',
        '--chapter=/', '--prefer-metadata-cover',
        '--no-chapters-in-toc', '--cover=cover.jpg', '--authors=Economist',
    ]


def _kindlegen(args: argparse.Namespace) -> ConversionCommand:
    binary = 'C:/Program Files (x86)/kindlegen/kindlegen.exe' if _is_windows() \
        else os.environ['HOME'] + '/bin/kindlegen'
    if args.kindle_gen:
        binary = str(args.kindle_gen)
        if not os.path.isfile(binary) and not binary.endswith('/kindlegen'):
            return None
    return [binary, 'economist.opf']
