import re

_non_alnum_regex = re.compile(r'\W')


def first_capitalize(word: str):
    if len(word):
        return word[0].upper() + word[1:]

    return word


def to_hashtag(text: str) -> str:
    """
    Преобразовать входной текст в текст, который можно использовать в качестве хештэга
    :param text: Входной текст
    :return: Строка хештега
    """
    split = _non_alnum_regex.split(text)

    return ''.join((
        first_capitalize(word) if i > 0 else word for i, word in enumerate((w for w in split if w))
    ))
