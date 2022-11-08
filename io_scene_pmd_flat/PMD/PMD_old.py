from typing import Tuple, List, BinaryIO
from enum import Enum

# import mathutils

import struct
import os
import sys


class PMD(object):
    @classmethod
    def from_file(cls, filename):
        with open(filename, "rb") as pmd_file:
            pmd = PMD()

            # METADATA
            magic = pmd_file.read(0x18).decode("ascii")
            pmd.version = magic[5:9]
            # TODO add 1.82 import support?
            if pmd.version != "1.83":
                raise Exception("only version 1.82 is supported, got " + pmd.version)
            pmd.type = ModelType(read_int(pmd_file.read(4)))
            pmd_file.read(4)

            # GIANT TABLES
            # offset and size
            offsets_table = [OffsetsTableElement() for i in range(37)]
            for off in offsets_table:
                off.offset = read_int(pmd_file.read(4))
                if off.offset > 0:
                    off.offset += 0x148

            for off in offsets_table:
                off.size = read_int(pmd_file.read(4))

            # BLOCKS

            # block 0
            pmd.block_0 = pmd.__load_vertices(pmd_file, offsets_table, 0)

            # block 1
            pmd.__load_polys(pmd_file, offsets_table)

            # block 2
            pmd.__load_uvs(pmd_file, offsets_table)

            # block 3
            pmd.vertices = pmd.__load_vertices(pmd_file, offsets_table, 3)

            # block 4
            pmd.faces = pmd.__load_faces(pmd_file, offsets_table, 4)

            # blocks 5 & 6
            pmd.__load_textures(pmd_file, offsets_table)

            # blocks 7 & 8
            # NOT a vert data, but also 4 floats, so...
            pmd.block_7 = pmd.__load_vertices(pmd_file, offsets_table, 7)
            pmd.__load_eight(pmd_file, offsets_table)

            # block 11
            pmd.__load_metadata(pmd_file, offsets_table)

            # block 9
            pmd.__load_transforms(pmd_file, offsets_table)

            # block 10
            pmd.__load_meshes(pmd_file, offsets_table)

            return pmd

    def __load_polys(self, pmd_file, offsets_table):
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[1].offset)
        polys_count = int(offsets_table[1].size / 0x8)
        self.polygons = [Poly(0, 0, 0, 0, 0) for i in range(polys_count)]
        for i in range(polys_count):
            (
                vert_count,
                material_index,
                uk,
                vertices_index,
                face_table_index,
            ) = struct.unpack("<BBhHH", pmd_file.read(0x8))
            self.polygons[i] = Poly(
                vert_count, material_index, uk, vertices_index, face_table_index
            )
        pmd_file.seek(current_cursor)

    # TODO load either in place or return list in all, make it uniform (and maybe universal?)
    def __load_uvs(self, pmd_file, offsets_table):
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[2].offset)
        uvs_count = int(offsets_table[2].size / 0x10)
        self.uvs = [UV(0, 0, 0, 0, 0) for i in range(uvs_count)]
        for i in range(uvs_count):
            u, v, vert_id, material_id, unknown = struct.unpack(
                "<ffHHL", pmd_file.read(0x10)
            )
            self.uvs[i] = UV(u, v, vert_id, material_id, unknown)

        pmd_file.seek(current_cursor)

    def __load_faces(self, pmd_file, offsets_table, index):
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[index].offset)
        faces_count = int(offsets_table[index].size / 0x2)
        faces_list = [0 for i in range(faces_count)]
        for i in range(faces_count):
            faces_list[i] = read_short(pmd_file.read(2))
        pmd_file.seek(current_cursor)
        return faces_list

    def __load_eight(
        self, pmd_file: BinaryIO, offsets_table: List[OffsetsTableElement]
    ):
        current_cursor = pmd_file.tell()
        sevens_number = int(offsets_table[8].size / 4)
        self.block_8 = [0 for i in range(sevens_number)]
        for i in range(sevens_number):
            pmd_file.seek(offsets_table[8].offset + (4 * i))
            self.block_8[i] = read_int(pmd_file.read(4)) + 0x148
        pmd_file.seek(current_cursor)

    def __load_textures(
        self, pmd_file: BinaryIO, offsets_table: List[OffsetsTableElement]
    ):
        current_cursor = pmd_file.tell()
        # TODO this is horrible way, onyl works for standard PMD files where the last element is just 0
        textures_number = int(offsets_table[6].size / 4) - 1
        self.textures = ["" for i in range(textures_number)]
        for i in range(textures_number):
            pmd_file.seek(offsets_table[6].offset + (4 * i))
            tex_name_offset = read_int(pmd_file.read(4)) + 0x148
            pmd_file.seek(tex_name_offset)
            while True:
                c = pmd_file.read(1)
                if c == b"\0":
                    break
                self.textures[i] += c.decode("ascii")
        pmd_file.seek(current_cursor)

    def __load_transforms(self, pmd_file, offsets_table):
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[9].offset)
        transforms_count = int(offsets_table[9].size / 0x50)
        # TODO better matrix representation
        self.transforms = [Transform(0, 0, 0, 0, 0) for i in range(transforms_count)]
        if transforms_count != self.meshes_in_lod:
            raise Exception(
                f"transforms count is different than in metadata: {transforms_count}!={self.meshes_in_lod}"
            )
        self.transforms = [0 for i in range(transforms_count)]
        for i in range(transforms_count):
            matrix_data = [0 for j in range(4)]
            for j in range(4):
                matrix_data[j] = [*struct.unpack("<4f", pmd_file.read(0x10))]
            matrix = matrix_data  # mathutils.Matrix(matrix_data)
            unknowns = struct.unpack("<4L", pmd_file.read(0x10))
            self.transforms[i] = Transform(matrix, *unknowns)
        pmd_file.seek(current_cursor)

    # block 10
    def __load_meshes(self, pmd_file, offsets_table):
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[10].offset)
        meshes_count = int(offsets_table[10].size / 0x40)
        if meshes_count != (len(self.lods) * self.meshes_in_lod):
            raise Exception(
                f"meshes count is different than in metadata: {meshes_count}!={len(self.lods) * self.meshes_in_lod}"
            )
        # I know, ugly, but the alternative is worse
        self.meshes = [0 for i in range(meshes_count)]
        for i in range(meshes_count):
            mesh_data = struct.unpack("<8H3Lf4H6L", pmd_file.read(0x40))
            self.meshes[i] = Mesh(*mesh_data)

        pmd_file.seek(current_cursor)


# TODO add this whole stuff to PMD, don't make two classes?
# food for thought
class Track(PMD):
    def __init__(self):
        self.type: ModelType = ModelType.Track
        # block 14 offset
        self.eof: int = 0
        self.block15 = []
        self.block16 = []
        self.block17 = []

        # size of block 20 divided by 0x90
        self.size_18: int = 0
        self.size_19: int = 0
        self.block20 = []
        # TODO merge these two?
        # AI curves, each is a list of 255 points, most tracks have 5 curves, chall1 is an exception
        self.ai_curves_data: List[List[Vertex]] = []
        self.ai_curves = []  # definitions
        self.block23 = []
        self.block24 = []
        self.block25 = []
        self.block26 = []
        self.block27 = []
        self.block28 = []
        self.block29 = []
        self.block30 = []
        self.block31 = []

        # static size of 0x38 bytes
        self.block32 = []
