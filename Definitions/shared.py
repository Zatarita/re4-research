import os


def read_int(stream, size : int):
    return int.from_bytes(stream.read(size), "little")


def create_save_directory(path):
    if not os.path.isdir(path):
        print("\tPath Not Found: Creating")
        os.makedirs(path)