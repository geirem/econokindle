import time

from urllib3 import PoolManager

from econokindle.Cache import Cache
from econokindle.KeyCreator import KeyCreator
from typing import List


class Fetcher:

    __timer = None
    __THROTTLE = 6

    def __init__(self, pool_manager: PoolManager, key_creator: KeyCreator, cache: Cache):
        self.__pool_manager = pool_manager
        self.__key_creator = key_creator
        self.__cache = cache
        if Fetcher.__timer is None:
            Fetcher.__timer = time.time()

    # Throttle downloads.
    @staticmethod
    def __throttle() -> None:
        if Fetcher.__timer is None:
            Fetcher.__timer = time.time()
            return
        remaining = Fetcher.__THROTTLE - time.time() + Fetcher.__timer
        if remaining < 0:
            return
        time.sleep(remaining)
        Fetcher.__timer = time.time()

    def fetch_page(self, url: str) -> str:
        cached = self.__cache.get(url)
        if cached is not None:
            return cached
        self.__throttle()
        result = self.__pool_manager.request("GET", url)
        if result.status != 200:
            raise Exception
        contents = result.data.decode("utf-8")
        if 'preloadedData' not in contents:
            raise FileNotFoundError
        self.__cache.store(url, contents)
        return contents

    def fetch_images(self, image_urls: str) -> List[bytes]:
        results = []
        for image in image_urls:
            results.append(self.fetch_image(image))
        return results

    def fetch_image(self, url: str) -> bytes:
        image = self.__cache.get(url)
        if not image:
            image = self.__pool_manager.request('GET', url, preload_content=False).read()
            self.__cache.store(url, image)
        return image
