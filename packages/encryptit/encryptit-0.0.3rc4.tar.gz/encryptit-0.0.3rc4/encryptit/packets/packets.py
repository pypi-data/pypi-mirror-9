import logging

import datetime
import struct

from enum import Enum
from collections import OrderedDict

from Crypto.Cipher.blockalgo import MODE_OPENPGP

from ..cipher_algorithms import decode_symmetric_cipher_algorithm
from ..mixins import SerializeNameOctetValueMixin
from ..string_to_key_specifiers import decode_string_to_key_specifier

from .packet_type import PacketType


LOG = logging.getLogger(__name__)


def create_packet(packet_type, header, body_octets, previous_packet, decoder):

    packet_classes = {
        PacketType.LiteralDataPacket:
        LiteralDataPacket,

        PacketType.SymmetricKeyEncryptedSessionKeyPacket:
        SymmetricKeyEncryptedSessionKeyPacket,

        PacketType.SymmetricEncryptedandIntegrityProtectedDataPacket:
        SymmetricEncryptedandIntegrityProtectedDataPacket,

        PacketType.SymmetricallyEncryptedDataPacket:
        SymmetricallyEncryptedDataPacket,
    }

    packet_cls = packet_classes[packet_type]

    return packet_cls(header, body_octets, previous_packet, decoder)


class Packet(object):
    def __init__(self, header_object, body_octets, previous_packet,
                 decoder):
        self.header = header_object
        self.body = body_octets
        self.previous_packet = previous_packet
        self.packet_decoder = decoder


class LiteralDataPacket(Packet):
    """
    Literal Data Packet (Tag 11)
    https://tools.ietf.org/html/rfc4880#section-5.9
    """

    class Format(SerializeNameOctetValueMixin, Enum):
        BINARY = 0x62
        TEXT = 0x74
        UTF8_TEXT = 0x75

    def serialize(self):
        return OrderedDict([
            ('formatting', self.formatting),
            ('filename', self.filename),
            ('date', self.date),
            ('raw_data', self.raw_data),
            ('decoded_data', self.decoded_data),
        ])

    @property
    def formatting(self):
        return LiteralDataPacket.Format(self.body[0])

    @property
    def filename_length(self):
        return self.body[1]

    @property
    def filename(self):
        return self.body[2:2 + self.filename_length].decode('utf-8')

    @property
    def date(self):
        offset = 2 + self.filename_length
        raw_date = self.body[offset:offset + 4]
        seconds = struct.unpack('I', raw_date)[0]
        if seconds == 0:
            return None
        else:
            return datetime.datetime.fromtimestamp(seconds)

    @property
    def raw_data(self):
        return self.body[2 + self.filename_length + 4:]

    @property
    def decoded_data(self):
        if self.formatting is LiteralDataPacket.Format.BINARY:
            return self.raw_data

        elif self.formatting is LiteralDataPacket.Format.TEXT:
            return self.raw_data.decode('ascii')

        elif self.formatting is LiteralDataPacket.Format.UTF8_TEXT:
            return self.raw_data.decode('utf-8')


class SymmetricallyEncryptedDataPacket(Packet):
    """
    5.7. Symetrically Encrypted Data Packet (Tag 9)
    https://tools.ietf.org/html/rfc4880#section-5.7

    plaintext:
    | random_iv  | repeated | plaintext_body |
    | block_size | 2 octets |                |

    encrypted data:
    | block_size | 2 octets | encrypted body |
    """

    def serialize(self):
        return OrderedDict([
            ('header', self.header),
            ('encrypted_iv', self.encrypted_iv),
            ('encrypted_body', self.encrypted_body),
            ('_decrypted_data', self.decrypted_data),
            ('subpackets', self.subpackets),
        ])

    @property
    def encrypted_data(self):
        return self.body

    @property
    def cipher_block_size(self):
        return self.previous_packet.cipher.block_size.in_octets

    @property
    def encrypted_iv(self):
        return self.body[0:self.cipher_block_size + 2]

    @property
    def encrypted_body(self):
        return self.body[self.cipher_block_size + 2:]

    @property
    def decrypted_data(self):
        """
        Note that currently we do not implement the "quick check".
        See https://github.com/paulfurley/encryptit/issues/2

        https://www.dlitz.net/software/pycrypto/api/current/
        Crypto.Cipher.blockalgo-module.html#MODE_OPENPGP
        """

        assert self.previous_packet is not None
        assert isinstance(self.previous_packet,
                          SymmetricKeyEncryptedSessionKeyPacket)

        key = self.previous_packet.session_key

        assert len(key) == self.previous_packet.cipher.key_length.in_octets

        cipher_context = self.previous_packet.cipher.new(
            key, MODE_OPENPGP, self.encrypted_iv)
        plaintext_data = cipher_context.decrypt(self.encrypted_body)

        assert plaintext_data[0:2] == bytes([0xcb, 0x18])

        with open('decrypted.gpg', 'wb') as f:
            f.write(plaintext_data)

        return plaintext_data

    @property
    def subpackets(self):
        return self.packet_decoder(self.decrypted_data)


class SymmetricEncryptedandIntegrityProtectedDataPacket(Packet):
    """
    5.13. Sym. Encrypted Integrity Protected Data Packet (Tag 18)
    http://tools.ietf.org/html/rfc4880#section-5.13
    """

    def serialize(self):
        return OrderedDict([
            ('header', self.header),
            ('version', self.version),
            ('encrypted_data', self.encrypted_data),
            ('_decrypted_data', self.decrypted_data),
        ])

    @property
    def version(self):
        version = self.body[0]
        assert version == 1
        return version

    @property
    def encrypted_data(self):
        return self.body[1:]

    @property
    def decrypted_data(self):
        return None


class SymmetricKeyEncryptedSessionKeyPacket(Packet):
    """
    5.3. Symmetric-Key Encrypted Session Key Packets (Tag 3)
    http://tools.ietf.org/html/rfc4880#section-5.3
    """
    def serialize(self):
        return OrderedDict([
            ('header', self.header),
            ('version', self.version),
            ('cipher', self.cipher),
            ('string_to_key_specifier', self.string_to_key_specifier),
            ('encrypted_session_key', self.encrypted_session_key),
            ('_session_key', self.session_key),
        ])

    @property
    def version(self):
        version = self.body[0]
        assert version == 4
        return version

    @property
    def cipher(self):
        return decode_symmetric_cipher_algorithm(self.body[1])

    @property
    def string_to_key_specifier(self):
        return decode_string_to_key_specifier(
            self.body[2], self.body[2:], self.cipher)

    @property
    def encrypted_session_key(self):
        """
        ... if the encrypted session key is not present... [which] can be
        detected on the basis of packet length and S2K specifier size ...
        """
        remaining = len(self.body[2:]) - len(self.string_to_key_specifier)
        if remaining == 0:
            return None

        else:
            assert remaining > 0
            return self.body[2:2 - remaining]

    @property
    def session_key(self):
        if self.encrypted_session_key:
            return self.decrypt_session_key_with_s2k_key(
                self.encrypted_session_key,
                self.string_to_key_specifier.key)
        else:
            return self.string_to_key_specifier.key

    @property
    def decrypt_session_key_with_s2k_key(encrypted_session_key, s2k_key):
        raise NotImplementedError
