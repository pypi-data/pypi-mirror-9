from nose.tools import assert_equal

from encryptit.hash_algorithms import MD5
from encryptit.cipher_algorithms import AES128, AES256

from encryptit.string_to_key_specifiers import calculate_required_hashers

TEST_DATA = [
    (AES128, MD5, 1),  # 16 octets, 16 octets
    (AES256, MD5, 2),  # 32 octets, 16 octets
]


def test_calculate_required_hashers():
    for cipher_algorithm, hash_algorithm, expected in TEST_DATA:
        yield (_check_required_hashers, cipher_algorithm, hash_algorithm,
               expected)


def _check_required_hashers(cipher_algorithm, hash_algorithm, expected):
    assert_equal(
        expected,
        calculate_required_hashers(cipher_algorithm, hash_algorithm))
