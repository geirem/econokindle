import time

import urllib3

from lib.Cache import Cache


class Fetcher:

    def __init__(self, pool_manager: urllib3.PoolManager, cache: Cache):
        self.__pool_manager = pool_manager
        self.__cache = cache

    def fetch(self, url: str) -> str:
        cached = self.__cache.get(url)
        if cached is not None:
            return cached
        time.sleep(6) # Throttle downloads.
        result = self.__pool_manager.request("GET", url)
        if result.status != 200:
            raise Exception
        contents = result.data.decode("utf-8")
        self.__cache.store(url, contents)
        return contents

    def fetch_image(self, url: str) -> None:
        cached = self.__cache.has(url)
        if cached:
            return
        r = self.__pool_manager.request('GET', url, preload_content=False)
        self.__cache.store(url, r)
