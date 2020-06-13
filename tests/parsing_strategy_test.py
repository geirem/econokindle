import pytest

from econokindle.KeyCreator import KeyCreator
from econokindle.ParsingStrategy import ParsingStrategy
from econokindle.TagParser import TagParser
from econokindle.parsers.ImgParser import ImgParser


@pytest.fixture(name='ps')
def create_ps() -> ParsingStrategy:
    class KeyCreatorMock(KeyCreator):
        def __init__(self):
            pass

    return ParsingStrategy(KeyCreatorMock(), [], [])


def test_that_it_finds_img_parser_for_a(ps: ParsingStrategy) -> None:
    img_parser = ps.get_parser({'name': 'img'})
    assert type(img_parser) is ImgParser


def test_that_it_defaults_to_tag_parser(ps: ParsingStrategy) -> None:
    default_parser = ps.get_parser({'name': 'nosuchtag'})
    assert type(default_parser) is TagParser
