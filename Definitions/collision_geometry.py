import os
import struct
from .shared import read_int


class CollisionLayer:
    _layer_header = 0x20

    class FaceGroup:
        def __init__(self, stream):
            self.bounding_box_position = (0, 0, 0)
            self.bounding_box_dimensions = (0, 0, 0)

            self.floor_face_count = 0
            self.ceiling_face_count = 0
            self.wall_face_count = 0

            self.node_format = 0
            self.node_size = 0

            self.floor_faces = []
            self.ceiling_faces = []
            self.wall_faces = []

            self.child_face_groups = []

            if stream:
                self.load(stream)

        def load(self, stream):
            start = stream.tell()
            self.bounding_box_position = struct.unpack("<fff", stream.read(0xC))
            self.bounding_box_dimensions = struct.unpack("<fff", stream.read(0xC))

            self.floor_face_count = read_int(stream, 2)
            self.ceiling_face_count = read_int(stream, 2)
            self.wall_face_count = read_int(stream, 2)

            self.node_format = read_int(stream, 2)  # 01: Parent; 02: Child
            self.node_size = read_int(stream, 4)    # size of all raw data (including child nodes if format is parent)

            self.floor_faces = list(
                struct.unpack(
                    "<" + ("H" * self.floor_face_count),
                    stream.read(2 * self.floor_face_count)
                )
            )

            self.ceiling_faces = list(
                struct.unpack(
                    "<" + ("H" * self.ceiling_face_count),
                    stream.read(2 * self.ceiling_face_count)
                )
            )

            self.wall_faces = list(
                struct.unpack(
                    "<" + ("H" * self.wall_face_count),
                    stream.read(2 * self.wall_face_count)
                )
            )

            # todo get recursive face groups to load


    class Face:
        def __init__(self, face_type: str, stream=None):
            self.vertex_indices = (0, 0, 0)
            self.face_normal = 0
            self.edge_indices = (0, 0, 0)
            self.type = face_type
            self.meta = None

            if stream:
                self.load(stream)

        def load(self, stream):
            self.vertex_indices = struct.unpack("<HHH", stream.read(0x6))
            self.face_normal = read_int(stream, 2)
            self.edge_indices = struct.unpack("<HHH", stream.read(0x6))
            stream.read(2)
            self.meta = stream.read(0x4)

    def __init__(self, stream=None):
        self.header = 0

        self.coordinate_count = 0
        self.normal_count = 0
        self.edge_count = 0
        self.unknown = 0
        self.total_faces = 0
        self.faces_floor = 0
        self.faces_ceiling = 0
        self.faces_walls = 0
        self.face_group_count = 0

        self.coordinates = []
        self.normals = []
        self.edges = []
        self.faces = []
        self.face_groups = []

        if stream:
            self.load(stream)

    def load(self, stream):
        self.header = read_int(stream, 2)
        if self.header != self._layer_header:
            print("Unable to Open File: Unknown Header")
            return

        self.coordinate_count = read_int(stream, 2)
        self.normal_count = read_int(stream, 2)
        self.edge_count = read_int(stream, 2)
        self.unknown = read_int(stream, 2)
        self.total_faces = read_int(stream, 2)
        self.faces_floor = read_int(stream, 2)
        self.faces_ceiling = read_int(stream, 2)
        self.faces_walls = read_int(stream, 2)
        self.face_group_count = read_int(stream, 2)

        self.coordinates = [struct.unpack("<fff", stream.read(0xC)) for x in range(self.coordinate_count)]
        self.normals = [struct.unpack("<fff", stream.read(0xC)) for x in range(self.normal_count)]
        self.edges = [struct.unpack("<fff", stream.read(0xC)) for x in range(self.edge_count)]

        self.faces = [self.Face("Floor", stream) for x in range(self.faces_floor)]
        self.faces += [self.Face("Ceiling", stream) for x in range(self.faces_ceiling)]
        self.faces += [self.Face("Wall", stream) for x in range(self.faces_walls)]




class CollisionGeometry:
    _collision_header = 0x80

    def __init__(self, path=None, stream=None):
        self.header = 0                                       # for container: 0x80, for layer: 0x20
        self.layer_count = 0                                  # how many layers are contained in the stream
        self.unknown = 0                                      # ?????

        self.layer_offsets = []                               # starting offsets for each layer as unsigned int
        self.collision_layers = []                            # array to hold each "CollisionLayer" in a container

        if path:
            self.load_file(path)                              # if a path has been passed, load from file

        if stream:
            self.load_stream(stream)                          # if a stream was passed, load from the stream

    def load_file(self, path: str):
        if not os.path.isfile(path):                          # verify files existence
            print(f"Unable to Locate Requested File: {path}")
            return False
        stream = open(path, "rb")                             # create a file stream handle
        self.load_stream(stream)                              # use it to load the file from stream
        return True

    def load_stream(self, stream):
        self.header = read_int(stream, 1)
        if self.header != self._collision_header:             # if file is just a layer
            stream.seek(stream.tell() - 1)                    # reset stream position
            self.collision_layers = [CollisionLayer(stream)]  # load the single layer
            return
        else:                                                 # else the file is a container
            self.layer_count = read_int(stream, 1)            # read the layer count from stream
            self.unknown = read_int(stream, 2)                # read unknown short from stream

            self.layer_offsets = list(
                struct.unpack(                                # Load the layer offsets
                    "<" + ("I" * self.layer_count),           # each an unsigned little endian integer. iiii
                    stream.read(4 * self.layer_count)         # layer_count amount of times
                )
            )
        return


SAT = CollisionGeometry  # SAT and EAT both have identical raw data.
EAT = CollisionGeometry  # The files only differ in how that data is interpreted