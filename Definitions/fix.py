import os
from shared import read_int, create_save_directory
import struct


class Entry:
    def __init__(self):
        self.index = None
        self.size = None
        self.offset = None
        self.data = None

    def load(self, stream):
        stream.seek(self.offset)
        self.data = stream.read(self.size)


class Fix:
    _header_entry_size = 12          # header entry consists of Index:Size:Offset 4 bytes each. 3 x 4 = 12
    _maximum_recursion_depth = 0x100 # infinite loop failsafe

    def __init__(self):
        self.entries = None

    def load(self, path):
        if not os.path.isfile(path):
            print(f"Unable to Open Requested File: {path}\n\tFile Not Found.")
            return False

        self.entries = []
        with open(path, "rb") as stream:
            for i in range(self._maximum_recursion_depth):
                new_entry = Entry()
                new_entry.index = read_int(stream, 4)
                # There is no count. The only way to know we've reached the end is to peek dds files' 4cc
                if new_entry.index == 0x20534444: # "dds "
                    break
                new_entry.size = read_int(stream, 4)
                new_entry.offset = read_int(stream, 4)
                print(f"{new_entry.index} - [{hex(new_entry.offset)}:{hex(new_entry.size)}]")
                self.entries.append(new_entry)

            for entry in self.entries:
                entry.load(stream)

            return True

    def update_header(self):
        if not self.entries:
            print("Unable to Update Header: No Entries Loaded.")

        # assume offsets are invalid and recalculate
        starting_offset = len(self.entries) * self._header_entry_size
        for index, entry in enumerate(self.entries):
            print(f"Updating Entry[{index}]:")
            entry.index = index             # update the index in case of item deletion
            print(f"\tIndex: {index}")
            entry.offset = starting_offset  # update data offset in case of item deletion/addition
            print(f"\tOffset: {starting_offset}")
            entry.size = len(entry.data)    # update the entry size in case of new dds data
            print(f"\tSize: {len(entry.data)}")
            starting_offset += entry.size   # adjust header offset position to account for this elements raw data

    def load_entry(self, path):
        if ".dds" not in path:
            print("File Must be .dds Texture")
            return False
        if not os.path.isfile(path):
            print("Unable to Locate Requested File")
            return False
        if not self.entries:
            self.entries = []

        print(f"Loading {path}:")
        new_entry = Entry()
        new_entry.data = open(path, "rb").read()
        new_entry.size = len(new_entry.data)
        print(f"\tSize: {new_entry.size}")
        new_entry.index = -1
        new_entry.offset = -1
        self.entries.append(new_entry)
        return True

    def remove_entry(self, index: int):
        for i in range(len(self.entries)):
            if self.entries[i].index != index:
                continue

            del self.entries[i]
            print(f"Removed Entry: {str(i)}")
            break

    def extract(self, path):
        # verify entries and save location
        if not self.has_entries():
            print("Unable to Extract Entries: None Have Been Loaded.")
            return False
        create_save_directory(path)

        # save the entries
        print(f'Saving {len(self.entries)} Textures to: "{path}"')
        for index, entry in enumerate(self.entries):
            print(f'\tFile {index} : {path}/{index}.dds')
            open(path + "/" + str(index) + ".dds", "wb").write(entry.data)
        return True

    def build(self, dest):
        print("Finalizing Header Data")
        self.update_header() # update any changes made to the data

        with open(dest, "wb") as stream:
            print("\nWriting Header...")
            self.write_header(stream)
            print("Writing Entries...")
            self.write_entries(stream)

    def has_entries(self):
        if self.entries:
            if len(self.entries) != 0:
                return True
        return False

    def write_header(self, stream):
        for entry in self.entries:
            stream.write(struct.pack("<III", entry.index, entry.size, entry.offset))

    def write_entries(self, stream):
        for entry in self.entries:
            stream.write(entry.data)


# utility
def fix_from_directory(src, dest):
    fix_file = Fix()
    # load each dds texture from the directory
    print(f"\nLoading Textures From '{src}'")
    for file in os.listdir(src):
        if ".dds" in file:
            fix_file.load_entry(src + "/" + file)
    # build the fix and save it to disk
    print("\nBuilding .fix to", dest, "...")
    fix_file.build(dest)
    print("Done!")


def extract_fix(src, dest):
    fix_file = Fix()
    print(f"\nLoading .fix From '{src}'")
    if not fix_file.load(src):
        print("~Aborting")
        return
    print(f"\nExtracting .fix To '{dest}'...")
    fix_file.extract(dest)
