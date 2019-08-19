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

    def _look_at_next_tag(self, tag: dict) -> Optional[str]:
        if 'children' not in tag:
            return None
        if tag['children']['type'] == 'text':
            return 'text'
        return tag['children']['name']
