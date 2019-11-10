import time
from urllib3 import PoolManager, HTTPResponse

from econokindle.Cookie import Cookie
from econokindle.CookieJar import CookieJar
from econokindle.Cache import Cache
from econokindle.KeyCreator import KeyCreator


class Fetcher:

    def __init__(self, pool_manager: PoolManager, key_creator: KeyCreator, cache: Cache):
        self.__pool_manager = pool_manager
        self.__key_creator = key_creator
        self.__cache = cache
        self.__cookie_jar = CookieJar()

    def fetch_page(self, url: str) -> str:
        cached = self.__cache.get(url)
        if cached is not None:
            return cached
        return self.__fetch_uncached(url)

    def __update_cookies(self, response: HTTPResponse) -> None:
        new_cookies = response.headers.get('set-cookie').split(',')
        for new_cookie in new_cookies:
            self.__cookie_jar.add(Cookie(new_cookie))

    def __fetch_uncached(self, url: str) -> str:
        while True:
            response = self.__pool_manager.request("GET", url)
            status = response.status
            if status == 200:
                self.__update_cookies(response)
                contents = response.data.decode("utf-8")
                if 'preloadedData' in contents:
                    self.__cache.store(url, contents)
                    return contents
            time.sleep(10)

    def fetch_image(self, url: str) -> bytes:
        image = self.__cache.get(url)
        if not image:
            image = self.__pool_manager.request('GET', url, preload_content=False).read()
            self.__cache.store(url, image)
        return image
