import argparse
import os
import platform
from shutil import copyfile


class Platform:

    def __init__(self):
        pass

    @staticmethod
    def kindle_gen_binary(args: argparse.Namespace) -> str:
        if args.kindle_gen:
            kindle_gen = args.kindle_gen
            if not os.path.isfile(kindle_gen) and not kindle_gen.endswith['/kindlegen']:
                raise FileNotFoundError
            return kindle_gen
        if platform.system() == 'Windows':
            return 'C:/Program Files (x86)/kindlegen/kindlegen.exe'
        return os.environ['HOME'] + '/bin/kindlegen'

    @staticmethod
    def load_to_kindle(work: str, edition: str) -> None:
        cached_name = work + 'economist.mobi'
        if platform.system() == 'Windows':
            root = 'D:/documents/'
        else:
            root = '/Volumes/Kindle/documents/'
        target_name = root + edition + '_economist.mobi'
        if os.path.isfile(root):
            copyfile(cached_name, target_name)
