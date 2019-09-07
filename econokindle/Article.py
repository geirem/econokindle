from econokindle import Fetcher, KeyCreator


class Article:

    def __init__(self, fetcher: Fetcher, key_creator: KeyCreator):
        self.__fetcher = fetcher
        self.__key_creator = key_creator
