from securitylib import advanced_crypto
from securitylib.advanced_crypto import validate_authenticator_key, validate_encryption_key

__all__ = ['generate_authenticator', 'validate_authenticator',
        'generate_encryption_key', 'generate_authenticator_key',
        'generate_encryption_key_from_password',
        'generate_authenticator_key_from_password', 'encrypt', 'decrypt']


def generate_authenticator(data, authenticator_key):
    """
    This function will generate an authenticator for the data (provides authentication and integrity).

    :param data: The data over which to generate the authenticator.
    :type data: :class:`str`

    :param authenticator_key: The secret key to be used by the function, in byte string.
                You can use :func:`~securitylib.crypto.generate_authenticator_key` to generate it.
    :type authenticator_key: :class:`str`

    :returns: :class:`str` -- The generated authenticator in byte string.
    """
    validate_authenticator_key(authenticator_key)
    return advanced_crypto.generate_authenticator(data, authenticator_key)


def validate_authenticator(data, authenticator_key, authenticator):
    """
    This function will generate an authenticator for the data using the given secret key
    and compare it to the given authenticator, in order to validate it.
    Use this function instead of performing the comparison yourself, because it
    avoids timing attacks.

    :param data: The data protected by the authenticator.
    :type data: :class:`str`

    :param authenticator_key: The secret key used to generate the given authenticator, in byte string.
    :type authenticator_key: :class:`str`

    :param authenticator: The authenticator you want to compare, in byte string.
    :type authenticator: :class:`str`

    :returns: :class:`bool` -- True if the given authenticator matches the generated authenticator or False otherwise.
    """
    validate_authenticator_key(authenticator_key)
    return advanced_crypto.validate_authenticator(data, authenticator_key, authenticator)


def generate_encryption_key():
    """
    Generates a key for use in the :func:`~securitylib.crypto.encrypt` and :func:`~securitylib.crypto.decrypt` functions.

    :returns: :class:`str` -- The generated key, in byte string.
    """
    return advanced_crypto.generate_encryption_key()


def generate_authenticator_key():
    """
    Generates an authenticator key.

    :returns: :class:`str` -- The generated key, in byte string.
    """
    return advanced_crypto.generate_authenticator_key()


def generate_encryption_key_from_password(password, salt):
    """
    Use this function to generate an encryption key from a password.

    :param password: The password from which to generate the key.
    :type password: :class:`str`

    :param salt: Salt for the password, in byte string.
                 You can use :func:`~securitylib.random.get_random_token` to generate it.
    :type salt: :class:`str`

    :returns: :class:`str` -- The generated encryption key, in byte string.
    """
    return advanced_crypto.generate_encryption_key_from_password(password, salt)


def generate_authenticator_key_from_password(password, salt):
    """
    Use this function to generate an authenticator key from a password.

    :param password: The password from which to generate the key.
    :type password: :class:`str`

    :param salt: Salt for the password, in byte string.
                 You can use :func:`~securitylib.random.get_random_token` to generate it.
    :type salt: :class:`str`

    :returns: :class:`str` -- The generated authenticator key, in byte string.
    """
    return advanced_crypto.generate_authenticator_key_from_password(password, salt)


def encrypt(data, key, authenticator_key):
    """
    Use this function to encrypt data.
    Two keys must be provided, one to guarantee confidentiality
    and another to guarantee integrity.

    :param data: The data to encrypt.
    :type data: :class:`str`

    :param key: The key to encrypt the data, in byte string. Provides confidentiality.
                You can use :func:`~securitylib.crypto.generate_encryption_key` to generate it.
    :type key: :class:`str`

    :param authenticator_key: The key to authenticate the data, in byte string. Provides integrity.
                              You can use :func:`~securitylib.crypto.generate_authenticator_key` to generate it.
    :type authenticator_key: :class:`str`

    :returns: :class:`str` -- The encrypted data.
    """
    validate_encryption_key(key)
    validate_authenticator_key(authenticator_key)
    return advanced_crypto.encrypt(data, key, authenticator_key)


def decrypt(ciphertext, key, authenticator_key):
    """
    Use this function to decrypt data that was encrypted using :func:`~securitylib.crypto.encrypt`.
    The same keys used to encrypt the data must be provided to decrypt it.

    :param ciphertext: The encrypted data.
    :type ciphertext: :class:`str`

    :param key: The key that was used to encrypt the data, in byte string.
    :type key: :class:`str`

    :param authenticator_key: The key that was used to authenticate the data, in byte string.
    :type authenticator_key: :class:`str`

    :returns: :class:`dict` -- The decrypted data.
    """
    validate_encryption_key(key)
    validate_authenticator_key(authenticator_key)
    return advanced_crypto.decrypt(ciphertext, key, authenticator_key)['data']
