import argparse
import os
import platform
import subprocess
from shutil import copyfile
from typing import Tuple, List, Optional, Union, Any


def load_to_kindle(work: str, issue: dict) -> None:
    cached_name = work + 'economist.mobi'
    cached_edition_name = work + issue['edition'] + '_economist.mobi'
    root = 'D:/documents/' if _is_windows() else '/Volumes/Kindle/documents/'
    target_name = root + issue['edition'] + '_economist.mobi'
    os.rename(cached_name, cached_edition_name)
    if os.path.isdir(root):
        copyfile(cached_edition_name, target_name)


def _is_macos() -> bool:
    return platform.system() == 'Darwin'


def _is_windows() -> bool:
    return platform.system() == 'Windows'


def convert_to_mobi(args: argparse.Namespace, path: str) -> None:
    if _is_macos():
        processor = _calibre_binary(args)
        subprocess.run([processor, 'economist.html', 'economist.mobi'], cwd=path)
    elif _is_windows():
        processor = _kindle_gen_binary(args)
        subprocess.run([processor, 'economist.opf'], cwd=path)
    if processor is None:
        print('No converter binary found, unable to render MOBI.')
        return
    subprocess.run(*processor, cwd=path)


def _calibre_binary(args: argparse.Namespace) -> Optional[Tuple[Union[str, Any], str, str]]:
    binary = '/Applications/calibre.app/Contents/MacOS/ebook-convert'
    if args.calibre:
        binary = args.calibre
        if not os.path.isfile(binary) and not binary.endswith['/ebook-convert']:
            return None
    return binary, 'economist.html', 'economist.mobi'


def _kindle_gen_binary(args: argparse.Namespace) -> Optional[Tuple[Union[str, Any], str]]:
    binary = 'C:/Program Files (x86)/kindlegen/kindlegen.exe' if _is_windows() else os.environ['HOME'] + '/bin/kindlegen'
    if args.kindle_gen:
        binary = args.kindle_gen
        if not os.path.isfile(binary) and not binary.endswith['/kindlegen']:
            return None
    return binary, 'economist.opf'
