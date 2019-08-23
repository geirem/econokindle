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
    def load_to_kindle(work: str) -> None:
        if platform.system() == 'Windows':
            if os.path.isfile('D:/documents'):
                copyfile(work + 'economist.mobi', 'D:/documents/economist.mobi')
        else:
            if os.path.isfile('/Volumes/Kindle'):
                copyfile(work + 'economist.mobi', '/Volumes/Kindle/documents/economist.mobi')
