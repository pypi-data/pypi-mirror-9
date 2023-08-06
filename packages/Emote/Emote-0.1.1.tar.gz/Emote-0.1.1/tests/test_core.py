"""
Unittests for emote.core
"""


import emote


def test_encode():

    for code in emote.CODES.keys():
        assert emote.lookup(code) == emote.CODES[code] == emote.lookup(':' + code + ':')


def test_encode_invalid_emoji():

    try:
        emote.lookup('__---___--Invalid__--__-Name')
        raise Exception("Above line should have raised a ValueError")
    except ValueError:
        pass


def test_decode():

    for name, u_code in emote.CODES.items():
        assert emote.decode(u_code) == name


def test_decode_invalid_string():

    try:
        emote.decode('__---___--Invalid__--__-Name')
        raise Exception("Above line should have raised a ValueError")
    except ValueError:
        pass
