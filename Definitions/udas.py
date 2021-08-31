import os
from shared import read_int


class Udas:
    _header_size = 0x400

    class entry:
        def __init__(self, stream):
            self.format = stream.read(3).decode("ascii") # Load file segment "four" cc
            stream.read(1)                               # Burn null terminator
            self.data = None

        def load(self, stream, offset : int, size : int):
            stream.seek(offset)                          # seek to the data offset
            self.data = stream.read(size)                # read the data from the file

    def __init__(self):
        self.header = None
        self.chunk_offsets = None
        self.entries = None

    def load(self, path : str):
        with open(path, "rb") as stream:
            filesize = len( stream.read() ) # used to calculate last chunk -> end
            stream.seek(0)

            self.header = stream.read(self._header_size) # unsure header; however, unneeded for extraction

            count = read_int(stream, 4)  # read segment count
            stream.read(0xC)             # burn padding
            print("Segments: ", count)

            self.chunk_offsets = [read_int(stream, 4) + self._header_size for x in range(count)] # read offsets
            self.chunk_offsets.append(filesize)

            self.entries = [self.entry(stream) for x in range(count)] # prime list with entries. acquire format

            for index, entry in enumerate(self.entries):
                if index - 1 == count: # if it's the last segment stop
                    break
                size = self.chunk_offsets[index + 1] - self.chunk_offsets[index] # segment size is next seg - current
                entry.load(stream, self.chunk_offsets[index], size)              # load the raw data for the segment
                print(f'\tSegment {index} - {entry.format}: [{size}b @ {hex(self.chunk_offsets[index])}]')

    def extract(self, path):
        print(f'Saving {len(self.entries)} Segments to: {path}')
        if not os.path.isdir(path):
            print("\tPath Not Found: Creating")
            os.makedirs(path)
        for index, file in enumerate(self.entries):
            print(f'\tSegment {index} - {file.format} : {path}/{index}.{file.format}')
            open(path + "/" + str(index) + "." + file.format, "wb").write(file.data)

    def save(self, path):
        pass # todo Figure out header and learn how to build Udas