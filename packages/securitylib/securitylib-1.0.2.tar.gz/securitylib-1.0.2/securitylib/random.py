from __future__ import absolute_import
import os
import string

import random
random = random.SystemRandom()

__all__ = ['get_random_bytes', 'get_random_integer', 'get_random_token', 'get_random_boolean', 'get_random_string', 'get_random_filename', 'get_random_GUID']


def get_random_bytes(length):
    """
    This function will generate strong random data for cryptographic usage.

    :param length: The length of the generated string of random bytes.
    :type length: :class:`int`

    :returns: :class:`str` -- The generated random bytes as a binary string.
    """
    return os.urandom(length)


def get_random_integer(min_result=0, max_result=65535):
    """
    Returns a random integer.

    :param min_result: The minimum number that can be generated.
    :type min_result: :class:`int`

    :param max_result: The maximum number that can be generated.
    :type max_result: :class:`int`

    :returns: :class:`int` -- The generated random number.
    """
    return random.randint(min_result, max_result)


def get_random_token(length=20):
    """
    Generate a random token that satisfies 2 properties: unique and unpredictable.

    :param length: The length of the token to be generated in bytes.
    :type length: :class:`int`

    :returns: :class:`str` -- The generated token (hex).

    Example:

    >>> random.get_random_token() # doctest: +SKIP
    '0f280bd84a4c6ae15c2deddec28c8e2e94b00dba'
    """
    return get_random_bytes(length).encode('hex')


def get_random_boolean():
    """
    Returns a random boolean value.

    :returns: :class:`bool` -- True or False.
    """
    return bool(random.getrandbits(1))


def get_random_string(length, charset=string.ascii_letters + string.digits):
    """
    Returns a random string based on the given length and the character set.

    :param length: The length of the random string to be generated.
    :type length: :class:`int`

    :param charset: The char set to be used (default is a-zA-Z0-9).
    :type charset: :class:`str`

    :returns: :class:`str` -- The generated random string.
    """
    if length < 1:
        raise ValueError('Parameter length must be at least 1.')
    if len(charset) < 2:
        raise ValueError('Parameter charset must have length at least 2.')

    return ''.join(random.choice(charset) for i in xrange(length))


def get_random_filename(length=12, extension=None, charset=string.ascii_lowercase + string.digits):
    """
    Returns a random filename based on the given length and extension.
    The dot between the filename and the extension is added automatically if
    an extension is given.

    :param length: The length of the random filename to be generated.
    :type length: :class:`int`

    :param extension: The extension to be appended to the filename.
    :type extension: :class:`str`

    :param charset: The char set to be used (default is a-z0-9).
    :type charset: :class:`str`

    :returns: :class:`str` -- The generated random filename.

    Example:

    >>> random.get_random_filename() # doctest: +SKIP
    'x7152s2lzbu5'
    >>> random.get_random_filename(8) # doctest: +SKIP
    'b2exn8ah'
    >>> random.get_random_filename(8, 'txt') # doctest: +SKIP
    '6fcldehx.txt'
    """
    filename = get_random_string(length, charset)
    if extension:
        return filename + '.' + extension
    else:
        return filename


def get_random_GUID():
    """
    Returns a random GUID.

    :returns: :class:`str` -- The generated GUID.

    Example:

    >>> random.get_random_GUID() # doctest: +SKIP
    'A7093430-468C-BBB6-ED70-DFF7B609B7A7'
    """
    guid_hex = get_random_bytes(16).encode('hex').upper()
    return '{0}-{1}-{2}-{3}-{4}'.format(guid_hex[0:8], guid_hex[8:12],
                                        guid_hex[12:16], guid_hex[16:20], guid_hex[20:32])
