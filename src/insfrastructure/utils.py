def to_hashtag(text: str) -> str:
    """
    Преобразовать входной текст в текст, который можно использовать в качестве хештэга
    :param text: Входной текст
    :return: Строка хештега
    """
    return ''.join((
        ch for ch in text if ch.isalnum()
    ))
