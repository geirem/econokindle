import time
from typing import Any

from urllib3 import PoolManager
from urllib3.exceptions import MaxRetryError

from econokindle.Cache import Cache
from econokindle.CookieJar import CookieJar
from econokindle.exceptions.RetrievalError import RetrievalError


class Fetcher:

    def __init__(self, pool_manager: PoolManager, cache: Cache):
        self.__pool_manager = pool_manager
        self.__cache = cache
        self.__cookie_jar = CookieJar()

    def fetch_page(self, url: str) -> str:
        return self.__cache.get(url) or self.__fetch_uncached(url)

    def __fetch_uncached(self, url: str) -> str:
        while True:
            try:
                response = self.__execute_request(url)
                contents = response.data.decode("utf-8")
                if '__NEXT_DATA__' in contents:
                    self.__cache.store(url, contents)
                    return contents
            except (MaxRetryError, RetrievalError):
                pass
            else:
                print('.', end='')
                time.sleep(10)

    def __cookies_as_header(self, url: str) -> str:
        return '; '.join(self.__cookie_jar.get_for_url(url))

    def __execute_request(self, url: str, preload_content=True) -> Any:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
        }
        cookies = self.__cookies_as_header(url)
        if cookies != "":
            headers['Cookie'] = cookies
        response = self.__pool_manager.request("GET", url, headers=headers, preload_content=preload_content)
        self.__cookie_jar.load_cookies(response)
        status = response.status
        if status != 200:
            raise RetrievalError()
        return response

    def fetch_image(self, url: str) -> bytes:
        image = self.__cache.get(url)
        if not image or len(image) < 1024:
            image = self.__execute_request(url, False).read()
            self.__cache.store(url, image)
        return image
