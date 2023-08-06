__author__ = 'netanelrevah'

import struct as _struct


class ParseObject(object):
    @classmethod
    def deserialize(cls, to_deserialize):
        return to_deserialize

    @staticmethod
    def serialize(to_serialize):
        return to_serialize

    @staticmethod
    def validate_deserialized(deserialized):
        pass

    @staticmethod
    def validate_serialized(deserialized):
        pass


class UnsignedByte(ParseObject):
    length = 1

    @classmethod
    def deserialize(cls, to_deserialize):
        return ord(to_deserialize)

    @staticmethod
    def serialize(to_serialize):
        return bytearray([to_serialize])

    @staticmethod
    def validate_deserialized(deserialized):
        assert 0 <= deserialized < 256, 'Unsigned byte must be between 0 to 256'


class UnsignedInt32(ParseObject):
    length = 4

    @classmethod
    def deserialize(cls, to_parse):
        return _struct.unpack('>I', to_parse)[0]

    @staticmethod
    def serialize(to_serialized):
        return _struct.pack('>I', to_serialized)