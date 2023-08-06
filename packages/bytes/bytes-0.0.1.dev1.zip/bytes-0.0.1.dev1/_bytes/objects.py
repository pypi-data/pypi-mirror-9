__author__ = 'netanelrevah'

import struct as _struct


class ParseObject(object):
    @classmethod
    def deserialize(cls, to_parse):
        return to_parse


class UnsignedByte(ParseObject):
    length = 1

    @classmethod
    def deserialize(cls, to_deserialize):
        return ord(to_deserialize)

    @classmethod
    def serialize(cls, to_serialize):
        return bytearray([to_serialize])

    @classmethod
    def validate_deserialized(cls, deserialized):
        assert 0 <= deserialized < 256, 'Unsigned byte must be between 0 to 256'


class UnsignedInt32(ParseObject):
    length = 4

    @classmethod
    def deserialize(cls, to_parse):
        return _struct.unpack('>I', to_parse)[0]