
""" ``comp`` module.
"""

import sys

from warnings import warn


PY3 = sys.version_info[0] >= 3

if PY3:  # pragma: nocover
    bytes_type = bytes
    str_type = str

    def chr(i):
        return bytes((i,))

    def ord(b):
        return b
else:  # pragma: nocover
    bytes_type = str
    str_type = unicode
    chr = chr
    ord = ord


if PY3:  # pragma: nocover
    def n(s, encoding='latin1'):
        if isinstance(s, str_type):
            return s
        return s.decode(encoding)

    def btos(b, encoding):
        return b.decode(encoding)

    def u(s):
        return s
else:  # pragma: nocover
    def n(s, encoding='latin1'):  # noqa
        if isinstance(s, bytes_type):
            return s
        return s.encode(encoding)

    def btos(b, encoding):  # noqa
        return b.decode(encoding)

    def u(s):
        return unicode(s, 'unicode_escape')


def b(s, encoding='latin1'):  # pragma: nocover
    if isinstance(s, bytes_type):
        return s
    return s.encode(encoding)


# Hash functions
try:  # pragma: nocover
    # Python 2.5+
    from hashlib import md5, sha1, sha224, sha256, sha384, sha512

    def digest_size(d):
        return d().digest_size

    try:
        from hashlib import new as openssl_hash

        def ripemd160():
            return openssl_hash('ripemd160')

        def whirlpool():
            return openssl_hash('whirlpool')
    except ValueError:
        ripemd160 = None
        whirlpool = None
except ImportError:  # pragma: nocover
    import md5  # noqa
    import sha as sha1  # noqa
    sha224 = sha256 = sha384 = sha512 = ripemd160 = whirlpool = None  # noqa

    def digest_size(d):
        return d.digest_size

# Encryption interface
block_size = None
encrypt = None
decrypt = None

# Supported cyphers
aes128 = None
aes192 = None
aes256 = None
aes128iv = None
aes192iv = None
aes256iv = None

# Python Cryptography Toolkit (pycrypto)
try:  # noqa pragma: nocover
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes

    # pycrypto interface

    def block_size(c):
        return c.block_size

    def encrypt(c, v):
        return c.encrypt(v)

    def decrypt(c, v):
        return c.decrypt(v)

    class AESIVCipher(object):
        """ AES cipher that uses random IV for each encrypt operation
            and prepend it to cipher text; decrypt splits input value into
            IV and cipher text.
        """
        block_size = 16

        def __init__(self, key):
            self.key = key

        def encrypt(self, v):
            iv = get_random_bytes(16)
            c = AES.new(self.key, AES.MODE_CBC, iv)
            return iv + c.encrypt(v)

        def decrypt(self, v):
            c = AES.new(self.key, AES.MODE_CBC, v[:16])
            return c.decrypt(v[16:])

    # suppored cyphers
    def aes(key, key_size=32):
        assert len(key) >= key_size
        if len(key) < key_size + 16:
            warn('AES%d: key and iv overlap.' % (key_size * 8))
        key = key[-key_size:]
        iv = key[:16]
        return lambda: AES.new(key, AES.MODE_CBC, iv)

    def aesiv(key, key_size=32):
        assert len(key) >= key_size
        c = AESIVCipher(key[:key_size])
        return lambda: c

    def aes128(key):
        return aes(key, 16)

    def aes192(key):
        return aes(key, 24)

    def aes256(key):
        return aes(key, 32)

    def aes128iv(key):
        return aesiv(key, 16)

    def aes192iv(key):
        return aesiv(key, 24)

    def aes256iv(key):
        return aesiv(key, 32)

except ImportError:  # pragma: nocover
    # TODO: add fallback to other encryption providers
    pass
