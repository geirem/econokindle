import time

from urllib3 import PoolManager

from econokindle.Cache import Cache
from econokindle.KeyCreator import KeyCreator


class Fetcher:

    __timer = None
    __THROTTLE = 6

    def __init__(self, pool_manager: PoolManager, key_creator: KeyCreator, cache: Cache, path: str):
        self.__pool_manager = pool_manager
        self.__key_creator = key_creator
        self.__cache = cache
        self.__path = path
        if Fetcher.__timer is None:
            Fetcher.__timer = time.time()

    # Throttle downloads.
    @staticmethod
    def __throttle() -> None:
        if Fetcher.__timer is None:
            Fetcher.__timer = time.time()
            return
        now = time.time()
        elapsed = time.time() - Fetcher.__timer
        remaining = Fetcher.__THROTTLE - elapsed
        print(f'Last timer was {Fetcher.__timer}.')
        print(f'Current timer is {now}.')
        print(f'Elapsed time is {elapsed}.')
        print(f'Remaining time to wait is {remaining}.')
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

    def fetch_images(self, image_urls: str) -> None:
        for image in image_urls:
            self.fetch_image(image)

    def fetch_image(self, url: str) -> None:
        image = self.__cache.get(url)
        if not image:
            image = self.__pool_manager.request('GET', url, preload_content=False).read()
            self.__cache.store(url, image)
        with open(self.__path + self.__key_creator.key(url), 'wb') as out:
            out.write(image)
