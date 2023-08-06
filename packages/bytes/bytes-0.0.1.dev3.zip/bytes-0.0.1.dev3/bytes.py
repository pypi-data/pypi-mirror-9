__author__ = 'code-museum'

from _bytes import objects


class DefinedSection(object):
    def __init__(self, name):
        self.name = name
        self.section = None
        self.times = None

    def is_(self, section):
        self.section = section
        self.times = 1

    def is_repeatedly(self, section, times=None):
        self.section = section
        self.times = times


class BytesSection(objects.BytesObject):
    def section(self, name):
        new_section = DefinedSection(name)
        self._defined_sections.append(new_section)
        return new_section

    def _define(self):
        raise NotImplementedError()

    def _define_when_needed(self):
        if not hasattr(self, 'defined_sections'):
            self._defined_sections = []
            self._define()

    @classmethod
    def serialize(cls, to_serialize):
        return to_serialize._serialize()

    def _serialize(self):
        self._define_when_needed()
        serialized = bytearray()
        for defined_section in self._defined_sections:
            serialized.extend(self._put(defined_section))
        return serialized

    def _put(self, defined_section):
        putted = bytearray()
        section_value = getattr(self, defined_section.name)
        section_value = [section_value] if defined_section.times == 1 else section_value
        for v in section_value:
            putted.extend(defined_section.section.serialize(v))
        return putted

    @classmethod
    def deserialize(cls, to_deserialize):
        parser = cls()
        parser._deserialize(to_deserialize)
        return parser

    def _deserialize(self, to_deserialize):
        self._define_when_needed()
        self._serialized_data = to_deserialize
        location = 0
        for defined_section in self._defined_sections:
            location, deserialized_section = self._take_repeatedly(defined_section, location)
            setattr(self, defined_section.name, deserialized_section)

    def _take_repeatedly(self, defined_section, location):
        repeat_list = []
        for _ in self._repeat_counter(defined_section.times):
            if location >= len(self._serialized_data):
                break
            read_data = self._take(defined_section, location)
            repeat_list.append(read_data)
            location += defined_section.section.length
        return location, repeat_list if len(repeat_list) > 1 else repeat_list[0]

    def _take(self, defined_section, location):
        parsed = defined_section.section.deserialize(
            self._serialized_data[location:location + defined_section.section.length])
        return parsed

    @staticmethod
    def _repeat_counter(times):
        if times:
            return range(times)

        def gen():
            while True:
                yield
        return gen()