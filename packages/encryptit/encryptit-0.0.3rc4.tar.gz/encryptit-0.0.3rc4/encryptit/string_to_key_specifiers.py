import logging
import math

from .compat import OrderedDict
from .hash_algorithms import decode_hash_algorithm, HashAlgorithm
from .cipher_algorithms import SymmetricCipherAlgorithm
from .mixins import SerializeNameOctetValueMixin

LOG = logging.getLogger(__name__)

_DECRYPTION_PASSPHRASE = 'foo'


def decode_string_to_key_specifier(octet_value, data, cipher):
    return OCTET_VALUE_TO_S2K_SPECIFIER[octet_value].decode(
        data, cipher, _DECRYPTION_PASSPHRASE)


def calculate_required_hashers(cipher, hash_algorithm):
    assert issubclass(cipher, SymmetricCipherAlgorithm), cipher
    assert issubclass(hash_algorithm, HashAlgorithm), hash_algorithm

    required_key_length = cipher.key_length.in_octets
    hash_length = hash_algorithm.length.in_octets

    num_hashers = int(math.ceil(float(required_key_length) / hash_length))

    LOG.debug('req. key length: {0}, hash_length: {0}, # hashers: {0}'.format(
        required_key_length, hash_length, num_hashers))

    assert num_hashers > 0
    return num_hashers


def make_preloaded_hashers(hash_algorithm, num_hashers):
    hashers = []
    for i in range(num_hashers):
        hasher = hash_algorithm.get_hasher()
        preloading_zeroes = bytes([0x0] * i)
        hasher.update(preloading_zeroes)
        hashers.append(hasher)
    return hashers


class StringToKeySpecifier(object):
    """
    3.7. String-to-Key (S2K) Specifiers
    http://tools.ietf.org/html/rfc4880#section-3.7
    """

    @property
    def value(self):
        return S2K_SPECIFIER_TO_OCTET_VALUE[self.__class__]

    @property
    def name(self):
        return self.__class__.__name__


class SimpleS2K(StringToKeySpecifier, SerializeNameOctetValueMixin):
    """
    3.7.1.1. Simple S2K
    http://tools.ietf.org/html/rfc4880#section-3.7.1.1
    """

    def __init__(self, hash_algorithm, cipher, passphrase):
        """
        passpharse is optional or None, in which case the key cannot be
        generated
        """
        self.hash_algorithm = hash_algorithm
        self.cipher = cipher
        self.passphrase = passphrase

    @classmethod
    def decode(cls, data, cipher, passphrase):
        assert data[0] == 0
        return cls(decode_hash_algorithm(data[1]), cipher, passphrase)

    def __len__(self):
        return 2

    def serialize(self):
        parent_dict = super(SimpleS2K, self).serialize()
        parent_dict.update(
            OrderedDict([
                ('hash_algorithm', self.hash_algorithm),
                ('_key', self.key),
            ]))
        return parent_dict

    @property
    def key(self):
        """
        Used *either*:
        1. To directly decrypt a subsequent encrypted data packet.
        2. To decrypt an encrypted session key, which then decrypts an
           encrypted data packet.
        """
        if _DECRYPTION_PASSPHRASE is None:
            return None

        num_hashers = calculate_required_hashers(

            self.cipher, self.hash_algorithm)

        hashers = make_preloaded_hashers(self.hash_algorithm, num_hashers)

        for hasher in hashers:
            hasher.update(_DECRYPTION_PASSPHRASE.encode('utf-8'))

        joined = b''.join([hasher.digest() for hasher in hashers])
        return joined[0: self.cipher.key_length.in_octets]


class SaltedS2K(StringToKeySpecifier):
    """
    3.7.1.2. Salted S2K
    http://tools.ietf.org/html/rfc4880#section-3.7.1.2
    """

    @classmethod
    def decode(cls, data, cipher):
        assert data[0] == 3
        raise NotImplementedError

    def __init__(self, hash_algorithm, salt, cipher):
        self.hash_algorithm = hash_algorithm
        self.salt = salt
        self.cipher = cipher


class IteratedAndSaltedS2K(object):
    """
    3.7.1.3. Iterated and Salted S2K
    http://tools.ietf.org/html/rfc4880#section-3.7.1.3
    """

    @classmethod
    def decode(cls, data, cipher):
        assert data[0] == 3
        raise NotImplementedError

    def __init__(self, hash_algorithm, salt, count, cipher):
        pass

    def __len__(self):
        return 11

    def serialize(self):
        parent_dict = super(IteratedAndSaltedS2K, self).serialize()
        parent_dict.update(
            OrderedDict([
                ('hash_algorithm', self.hash_algorithm),
                ('salt', self.salt),
                ('octet_count', self.octet_count),
            ]))
        return parent_dict

    @property
    def hash_algorithm(self):
        return decode_hash_algorithm(self.data[1])

    @property
    def salt(self):
        salt = self.data[2:10]
        assert len(salt) == 8
        return salt

    @property
    def octet_count(self):
        return self.data[10]

    @property
    def calculated_session_key(self):
        raise NotImplementedError


OCTET_VALUE_TO_S2K_SPECIFIER = {
    0: SimpleS2K,
    1: SaltedS2K,
    3: IteratedAndSaltedS2K,
}

S2K_SPECIFIER_TO_OCTET_VALUE = dict(
    [(v, k) for k, v in OCTET_VALUE_TO_S2K_SPECIFIER.items()]
)
