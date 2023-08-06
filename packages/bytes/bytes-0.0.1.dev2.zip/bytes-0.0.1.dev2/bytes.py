__author__ = 'code-museum'
__version__ = '0.0.1.dev2'

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


class ParseSection(objects.ParseObject):
    def _take(self, defined_section, location):
        parsed = defined_section.section.deserialize(
            self._serialized_data[location:location + defined_section.section.length])
        return parsed

    def _take_repeatedly(self, defined_section, location):
        repeat_list = []
        for _ in self._repeat_counter(defined_section.times):
            if location >= len(self._serialized_data):
                break
            read_data = self._take(defined_section, location)
            repeat_list.append(read_data)
            location += defined_section.section.length
        return location, repeat_list if len(repeat_list) > 1 else repeat_list[0]

    @classmethod
    def deserialize(cls, to_deserialize):
        parser = cls()
        parser._deserialize(to_deserialize)
        return parser

    @staticmethod
    def serialize(to_serialize):
        return to_serialize._serialize()

    def _serialize(self):
        if not hasattr(self, 'defined_sections'):
            self._defined_sections = []
            self._define()
        serialized = []
        for defined_section in self._defined_sections:
            serialized += self.put_repeatedly(defined_section)
        return b''.join(serialized)

    def put_repeatedly(self, defined_section):
        putted = []
        value = getattr(self, defined_section.name)
        if defined_section.times == 1:
            putted.append(defined_section.section.serialize(value))
        else:
            for v in value:
                putted.append(defined_section.section.serialize(v))
        return putted

    def _deserialize(self, to_deserialize):
        if not hasattr(self, 'defined_sections'):
            self._defined_sections = []
            self._define()
        self._serialized_data = to_deserialize
        location = 0
        for defined_section in self._defined_sections:
            location, deserialized_section = self._take_repeatedly(defined_section, location)
            setattr(self, defined_section.name, deserialized_section)

    def _define(self):
        raise NotImplementedError()

    @staticmethod
    def _repeat_counter(times):
        if times:
            return range(times)

        def gen():
            while True:
                yield
        return gen()

    def section(self, name):
        new_section = DefinedSection(name)
        self._defined_sections.append(new_section)
        return new_section