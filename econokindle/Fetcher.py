import time

import urllib3

from econokindle.Cache import Cache


class Fetcher:

    def __init__(self, pool_manager: urllib3.PoolManager, cache: Cache):
        self.__pool_manager = pool_manager
        self.__cache = cache

    def fetch_page(self, url: str) -> str:
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

    def fetch_images(self, image_urls: str) -> None:
        for image in image_urls:
            self.fetch_image(image)

    def fetch_image(self, image_url: str) -> None:
        cached = self.__cache.has(image_url)
        if cached:
            return
        r = self.__pool_manager.request('GET', image_url, preload_content=False)
        self.__cache.store(image_url, r)
