import unittest
from typing import Any, Optional

import urllib3

from econokindle.Cache import Cache
from econokindle.Fetcher import Fetcher
from econokindle.KeyCreator import KeyCreator


class CacheMock(Cache):
    def __init__(self, key_creator: KeyCreator):
        super().__init__(key_creator)
        self.__contents = None

    def get(self, document: str) -> Optional[str]:
        return self.__contents

    def store(self, document: str, contents: Any) -> None:
        self.__contents = contents


class KeyCreatorMock(KeyCreator):
    pass


class PoolMock(urllib3.PoolManager):
    def request(self, method, url, **kwargs):
        raise Exception('Method call not expected.')


class FetcherTest(unittest.TestCase):

    def setUp(self) -> None:
        self.__key_creator = self.__create_key_creator_mock()
        self.__cache = self.__create_cache_mock()
        self.__pool = self.__create_pool_mock()
        self.__fetcher = Fetcher(self.__pool, self.__key_creator, self.__cache)

    def __create_cache_mock(self) -> Cache:
        return CacheMock(self.__key_creator)

    @staticmethod
    def __create_key_creator_mock() -> KeyCreator:
        return KeyCreatorMock('/')

    @staticmethod
    def __create_pool_mock() -> urllib3.PoolManager:
        return PoolMock()

    def test_that_we_skip_download_on_cache_hit(self):
        document = 'https://foo.example.org/hit'
        contents = 'some contents'
        self.__cache.store(document, contents)
        self.__fetcher.fetch_page(document)
