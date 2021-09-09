from shared import read_int, create_save_directory
import os
import struct

class Entry:
    def __init__(self):
        self.ID = None
        self.size = None
        self.neg = -1
        self.format = None

        self.data = None

    def load(self, stream):
        self.size = read_int(stream, 4)
        self.neg = read_int(stream, 4, sign=True)
        self.ID = read_int(stream, 4)
        self.format = read_int(stream, 4)

        if self.neg > 0: print(f"If you are seeing this lemme know: {self.ID}")

        self.data = stream.read(self.size)

class Pack:
    def __init__(self):
        self.ID = None
        self.entries = None

    def load(self, path):
        if not os.path.isfile(path):
            print(f"Unable to Open Requested File: {path}\n\tFile Not Found.")
            return False

        self.entries = []
        with open(path, "rb") as stream:
            self.ID = read_int(stream, 4)
            entry_count = read_int(stream, 4)
            offsets = [read_int(stream, 4) for x in range(entry_count)]
            for offset in offsets:
                stream.seek(offset)
                new_entry = Entry()
                new_entry.load(stream)
                self.entries.append(new_entry)
            return True

    def extract(self, path):
        if not self.entries:
            print("Unable to Extract Entries: None Have Been Loaded.")
            return False
        create_save_directory(path)

        print(f'Saving {len(self.entries)} Textures to: "{path}"')
        for index, entry in enumerate(self.entries):
            print(f'\tFile {index} : {path}/{index}.{"tga" if entry.format == 0 else ".dds"}')
            open(path + "/" + str(index) + (".tga" if entry.format == 0 else ".dds"), "wb").write(entry.data)
        return True