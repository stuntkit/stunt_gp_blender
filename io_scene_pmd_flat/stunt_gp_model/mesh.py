"""This module store everything connected to a sigular mesh"""

import struct
from typing import BinaryIO

from .offsetstable import OffsetsTable


class Mesh:  # 1_83:
    """A singular mesh"""

    # pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-locals
    def __init__(
        self,
        uk: int,
        uk2: int,
        uk3: int,
        uk4: int,
        transform_index: int,
        uk5: int,
        uk6: int,
        uk7: int,
        uk8: int,
        uk9: int,
        uk10: int,
        weight: float,
        uk_index: int,
        uk_index2: int,
        polys_count: int,
        uvs_count: int,
        verts_count: int,
        uvs_start_index: int,
        verts_start_index: int,
        polys_start_index: int,
        uk11: int,
        uk12: int,
    ):
        self.unknown: int = uk
        self.unknown2: int = uk2
        self.unknown3: int = uk3
        self.unknown4: int = uk4
        self.transform_index: int = transform_index
        self.unknown5: int = uk5
        self.unknown6: int = uk6
        self.unknown7: int = uk7
        self.unknown8: int = uk8
        self.unknown9: int = uk9
        self.unknown10: int = uk10
        self.weight: float = weight
        self.uk_index: int = uk_index
        self.uk_index2: int = uk_index2
        self.polys_count: int = polys_count
        self.uvs_count: int = uvs_count
        self.verts_count: int = verts_count
        self.uvs_start_index: int = uvs_start_index
        self.verts_start_index: int = verts_start_index
        self.polys_start_index: int = polys_start_index
        self.unknown11: int = uk11
        self.unknown12: int = uk12

    @staticmethod
    def parse_mesh_1_60(
        pmd_file: BinaryIO,
        offsets_table: OffsetsTable,
        table_index: int,
        mesh_index: int,
    ) -> "Mesh":
        raise Exception("Unimplemented mesh")
        pass

    @staticmethod
    def parse_mesh_1_82(
        pmd_file: BinaryIO,
        offsets_table: OffsetsTable,
        table_index: int,
        mesh_index: int,
    ) -> "Mesh":
        raise Exception("Unimplemented mesh")
        pass

    @staticmethod
    def parse_mesh_1_83(
        pmd_file: BinaryIO,
        offsets_table: OffsetsTable,
        table_index: int,
        mesh_index: int,
    ) -> "Mesh":
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset + (0x40 * mesh_index))
        mesh_data = struct.unpack("<8H3Lf4H6L", pmd_file.read(0x40))
        mesh = Mesh(*mesh_data)
        pmd_file.seek(current_cursor)
        return mesh

    @staticmethod
    def parse_meshes_1_60(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["Mesh"]:
        meshes: list["Mesh"] = []
        meshes_count = int(offsets_table[table_index].size / 44)
        for i in range(meshes_count):
            meshes.append(Mesh.parse_mesh_1_60(pmd_file, offsets_table, table_index, i))
        return meshes

    @staticmethod
    def parse_meshes_1_82(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["Mesh"]:
        meshes: list["Mesh"] = []
        meshes_count = int(offsets_table[table_index].size / 60)
        for i in range(meshes_count):
            meshes.append(Mesh.parse_mesh_1_82(pmd_file, offsets_table, table_index, i))
        return meshes

    @staticmethod
    def parse_meshes_1_83(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["Mesh"]:
        meshes: list["Mesh"] = []
        meshes_count = int(offsets_table[table_index].size / 64)
        for i in range(meshes_count):
            meshes.append(Mesh.parse_mesh_1_83(pmd_file, offsets_table, table_index, i))
        return meshes
