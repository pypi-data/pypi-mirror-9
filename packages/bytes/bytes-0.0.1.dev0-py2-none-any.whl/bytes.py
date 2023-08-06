__author__ = 'netanelrevah'

from _bytes import objects


# class ParseEnum(object):
#     pass


class ParseSection(object):
    def __init__(self, data):
        self._data = data
        self._location = 0

    # @property
    # def parsed_data(self):
    #     return self._data

    def take(self, section):
        parsed = section.parse(self._data[self._location:self._location + section.length])
        self._location += section.length
        return parsed

    def repeat(self, section, times=None):
        repeat_list = []
        for _ in self._repeat_counter(times):  # self._repeat_counter(times):
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




    # def _parse(self):
    #     self.value = ord(self._data)

    # def fetch(self):
    #     self.source_bytes = io.read(self.length)
    # pass





# class LinkLayerType(unsigned_int_32):
#     pass


# class CapturedPacketHeader(ParseSection):
#     def _parse(self):
#         self.seconds = self.take(unsigned_int_32)
#         self.micro_seconds = self.take(unsigned_int_32)
#         self.data_len = self.take(unsigned_int_32)
#         self.original_length = self.take(unsigned_int_32)


# class CapturedPacket(ParseSection):
#     def _parse(self):
#         self.header = self.take(CapturedPacketHeader)
#         self.data = self.repeat(section=unsigned_byte, times=self.header.data_len)
#     pass


# class GeneralHeader(ParseSection):
#     def _parse(self):
#         self.magic = self.take(unsigned_int_32)
#         self.link_layer_type = self.take(LinkLayerType)
#     pass


# class CaptureFile(ParseSection):
#     def _parse(self):
#         self.header = self.take(section=GeneralHeader)
#         self.packets = self.repeat(section=CapturedPacket, times=None)
#     pass


# if __name__ == "__main__":
#     f = open('some_capture_file.cap')
#     capture_file = CaptureFile.parse(f)
#     assert isinstance(GeneralHeader, capture_file.header)
#     assert isinstance(tuple, capture_file.packets)