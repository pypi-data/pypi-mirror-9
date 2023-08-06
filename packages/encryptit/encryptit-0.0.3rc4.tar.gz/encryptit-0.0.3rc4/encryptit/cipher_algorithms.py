from .compat import OrderedDict

from Crypto.Cipher import AES as AES_cipher

from .length import Length


def decode_symmetric_cipher_algorithm(octet):
    return OCTET_VALUE_TO_ALGORITHM[octet]


class SymmetricCipherAlgorithm():
    """
    9.2. Symmetric-Key Algorithms
    http://tools.ietf.org/html/rfc4880#section-9.2
    """

    def __init__(self):
        raise RuntimeError('SymmetricCipherAlgorithm must not be '
                           'instantiated')

    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def octet_value(cls):
        return ALGORITHM_TO_OCTET_VALUE[cls]

    @classmethod
    def serialize(cls):
        return OrderedDict([
            ('name', cls.name()),
            ('octet_value', cls.octet_value()),
            ('key_length', cls.key_length),
            ('block_size', cls.block_size),
        ])


class UNENCRYPTED(SymmetricCipherAlgorithm):
    pass


class IDEA(SymmetricCipherAlgorithm):
    pass


class TRIPLEDES(SymmetricCipherAlgorithm):
    pass


class CAST5(SymmetricCipherAlgorithm):
    pass


class BLOWFISH(SymmetricCipherAlgorithm):
    pass


class AES128(SymmetricCipherAlgorithm):
    new = AES_cipher.new
    key_length = Length(bits=128)
    block_size = Length(bits=128)


class AES192(SymmetricCipherAlgorithm):
    new = AES_cipher.new
    key_length = Length(bits=192)
    block_size = Length(bits=128)


class AES256(SymmetricCipherAlgorithm):
    new = AES_cipher.new
    key_length = Length(bits=256)
    block_size = Length(bits=128)


class TWOFISH(SymmetricCipherAlgorithm):
    pass


OCTET_VALUE_TO_ALGORITHM = {
    0: UNENCRYPTED,
    1: IDEA,
    2: TRIPLEDES,
    3: CAST5,
    4: BLOWFISH,
    7: AES128,
    8: AES192,
    9: AES256,
    10: TWOFISH,
}

ALGORITHM_TO_OCTET_VALUE = dict(
    [(v, k) for k, v in OCTET_VALUE_TO_ALGORITHM.items()]
)
