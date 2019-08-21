import unittest

import urllib3

from lib.Cache import Cache
from lib.Fetcher import Fetcher


class FetcherTest(unittest.TestCase):

    def setUp(self) -> None:
        self.__cache = self.cache_mock('/', 1)
        self.__pool = self.pool_mock()
        self.__fetcher = Fetcher(self.__pool, self.__cache)

    @staticmethod
    def cache_mock(path: str, max_age: int) -> Cache:
        class CacheMock(Cache):
            pass
        return CacheMock(path, max_age)

    @staticmethod
    def pool_mock() -> urllib3.PoolManager:
        class PoolMock(urllib3.PoolManager):
            pass
        return PoolMock()

    def test_that_we_skip_download_on_cache_hit(self):
        self.__fetcher = Fetcher(self.__pool, self.__cache)


if __name__ == '__main__':
    import xmlrunner

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False,
        buffer=False,
        catchbreak=False)
