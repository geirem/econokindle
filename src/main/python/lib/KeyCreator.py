import datetime


class KeyCreator:

    def __init__(self):
        pass

    @staticmethod
    def key(document: str) -> str:
        key = document.split('/').pop()
        if key == '' or key is None:
            key = 'index'
        return str(datetime.date.today()) + '_' + key
