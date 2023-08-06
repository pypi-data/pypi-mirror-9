__author__ = 'code-museum'
__version__ = '0.0.1.dev1'

objects = __import__('_bytes.objects', fromlist='objects')


class ParseSection(object):
    def __init__(self, data):
        self._data = data
        self._location = 0

    def take(self, section):
        parsed = section.deserialize(self._data[self._location:self._location + section.length])
        self._location += section.length
        return parsed

    def repeat(self, section, times=None):
        repeat_list = []
        for _ in self._repeat_counter(times):
            if self._location == len(self._data):
                break
            read_data = self.take(section)
            repeat_list.append(read_data)
        return repeat_list

    @classmethod
    def parse(cls, to_parse):
        parser = cls(to_parse)
        parser._parse()
        return parser

    def _parse(self):
        raise NotImplementedError()

    @staticmethod
    def _repeat_counter(times):
        if times:
            return range(times)

        def gen():
            while True:
                yield
        return gen()