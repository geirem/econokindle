from typing import Optional

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

    @staticmethod
    def _peek_at_first_child(tag: dict) -> Optional[dict]:
        if 'children' not in tag:
            return None
        children = tag['children']
        if len(children) == 0:
            return None
        return children[0]
