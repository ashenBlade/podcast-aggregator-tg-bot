import pytest as pytest

from insfrastructure.utils import to_hashtag


@pytest.mark.parametrize('text,expected', [
    ('asdf', 'asdf'),
    ('a', 'a'),
    ('ЯндексПодкасты', 'ЯндексПодкасты'),
    ('GoogleПодкасты', 'GoogleПодкасты'),
    ('GoogleПодкасты2', 'GoogleПодкасты2'),
    ('Подкаст69', 'Подкаст69'),
])
def test__when_all_alphanumeric_chars__should_return_same_string(text, expected):
    actual = to_hashtag(text)
    assert actual == expected


@pytest.mark.parametrize('text,expected', [
    ('A A', 'AA'),
    ('Яндекс.Музыка', 'ЯндексМузыка'),
    ('Google Подкасты', 'GoogleПодкасты'),
    ('Пилим,Трем', 'ПилимТрем')
])
def test__should_remove_non_alphanumeric(text, expected):
    actual = to_hashtag(text)
    assert actual == expected
