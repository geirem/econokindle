import time

from urllib3 import PoolManager

from econokindle.Cache import Cache
from econokindle.KeyCreator import KeyCreator


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
        print(f'Last timer was {Fetcher.__timer}.')
        now = time.time()
        print(f'Current timer is {now}.')
        print(f'Elapsed time is {now - Fetcher.__timer}.')
        print(f'Remaining time to wait is {Fetcher.__THROTTLE - now + Fetcher.__timer}')
        if Fetcher.__timer is None:
            Fetcher.__timer = time.time()
            return
        time_to_sleep = Fetcher.__THROTTLE - (time.time() - Fetcher.__timer)
        Fetcher.__timer = time.time()
        if time_to_sleep < 0:
            return
        time.sleep(time_to_sleep)

    def fetch_page(self, url: str) -> str:
        cached = self.__cache.get(url)
        if cached is not None:
            return cached
        self.__throttle()
        result = self.__pool_manager.request("GET", url)
        if result.status != 200:
            raise Exception
        contents = result.data.decode("utf-8")
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
        with open(self.__key_creator.key((url)), 'wb') as out:
            out.write(image)
