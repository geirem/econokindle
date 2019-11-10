class Cookie:

    def __init__(self, cookie):
        self.__raw_cookie = cookie
        parts = cookie.split(';')
        for part in parts:
            key, value = part.split('=')

    def applies_to(self, url: str) -> bool:
        return True
