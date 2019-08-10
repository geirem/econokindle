class KeyCreator:

    def __init__(self):
        pass

    @staticmethod
    def key(document: str) -> str:
        key = document.split('/').pop()
        if key == '' or key is None:
            return 'index'
        return key
