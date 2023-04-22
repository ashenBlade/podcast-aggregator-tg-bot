import pytest as pytest

from insfrastructure.utils import to_hashtag


@pytest.mark.parametrize('text,expected', [
    ('asdf', 'asdf'),
    ('a', 'a'),
    ('Яндекс Подкасты', 'ЯндексПодкасты'),
    ('Google Подкасты', 'GoogleПодкасты'),
    ('Google Подкасты 2', 'GoogleПодкасты2'),
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


@pytest.mark.parametrize('text, expected', [
    ('Яндекс подкасты', 'ЯндексПодкасты'),
    ('Мысли и методы', 'МыслиИМетоды'),
    ('Завтракаст', 'Завтракаст'),
    ('Разбор полетов', 'РазборПолетов'),
    ('IT Way Podcast', 'ITWayPodcast'),
    ('Moscow python', 'MoscowPython'),
    ('Как делают игры', 'КакДелаютИгры'),
    ('Релиз в пятницу', 'РелизВПятницу'),
    ('Веб-стандарты', 'ВебСтандарты')
])
def test__should_capitalize_first_letter__when_space_between(text, expected):
    actual = to_hashtag(text)
    assert actual == expected
