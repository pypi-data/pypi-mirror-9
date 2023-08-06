__author__ = 'netanelrevah'

import struct as _struct


class BytesObject(object):
    @classmethod
    def deserialize(cls, to_deserialize):
        return to_deserialize

    @classmethod
    def serialize(cls, to_serialize):
        return to_serialize

    @staticmethod
    def validate_deserialized(deserialized):
        pass

    @staticmethod
    def validate_serialized(deserialized):
        pass


class UnsignedByte(BytesObject):
    length = 1

    @classmethod
    def deserialize(cls, to_deserialize):
        return ord(to_deserialize)

    @classmethod
    def serialize(cls, to_serialize):
        return bytearray([to_serialize])

    @staticmethod
    def validate_deserialized(deserialized):
        assert 0 <= deserialized < 256, 'Unsigned byte must be between 0 to 256'


class StructBytesObject(BytesObject):
    struct_format = ''

    @classmethod
    def deserialize(cls, to_deserialize):
        return _struct.unpack(cls.struct_format, to_deserialize)[0]

    @classmethod
    def serialize(cls, to_serialized):
        return _struct.pack(cls.struct_format, to_serialized)


class UnsignedInt32(StructBytesObject):
    length = 4
    struct_format = '>I'


class BigEndianUnsignedInt32(StructBytesObject):
    length = 4
    struct_format = '<I'