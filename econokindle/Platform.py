import argparse
import os
import platform
import subprocess
from shutil import copyfile


class Platform:

    @staticmethod
    def __kindle_gen_binary(args: argparse.Namespace) -> str:
        if args.kindle_gen:
            kindle_gen = args.kindle_gen
            if not os.path.isfile(kindle_gen) and not kindle_gen.endswith['/kindlegen']:
                raise FileNotFoundError
            return kindle_gen
        if platform.system() == 'Windows':
            return 'C:/Program Files (x86)/kindlegen/kindlegen.exe'
        return os.environ['HOME'] + '/bin/kindlegen'

    @staticmethod
    def load_to_kindle(work: str, issue: dict) -> None:
        if Platform.__is_macos():
            print('Catalina is not supported, not loading mobi.')
            return
        cached_name = work + 'economist.mobi'
        cached_edition_name = work + issue['edition'] + '_economist.mobi'
        if platform.system() == 'Windows':
            root = 'D:/documents/'
        else:
            root = '/Volumes/Kindle/documents/'
        target_name = root + issue['edition'] + '_economist.mobi'
        os.rename(cached_name, cached_edition_name)
        if os.path.isdir(root):
            copyfile(cached_edition_name, target_name)

    @staticmethod
    def __is_macos() -> bool:
        return platform.system() == 'Darwin'

    @staticmethod
    def convert_to_mobi(args: argparse.Namespace, path: str) -> None:
        if Platform.__is_macos():
            print('Catalina is not supported, not rendering mobi.')
            return
        kindle_gen = Platform.__kindle_gen_binary(args)
        subprocess.run([kindle_gen, 'economist.opf'], cwd=path)
