from lib import KeyCreator


class TagParser:

    def __init__(self, key_creator: KeyCreator, images: list, valid_references: list):
        self._key_creator = key_creator
        self._images = images
        self._valid_references = valid_references

    def parse(self, tag: dict) -> dict:
        name = tag['name']
        return {
            'open': f'<{name}>',
            'close': f'</{name}>',
        }
