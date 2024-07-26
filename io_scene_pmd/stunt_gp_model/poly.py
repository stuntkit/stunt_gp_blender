"""This module stores classes handling polygons"""

from typing import BinaryIO
import struct

from .offsetstable import OffsetsTable


class Polygon:
    """A singular polygon"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        vertices_count: int = 0,
        material_index: int = 0,
        unknown: int = 0,
        unknown2: int = 0,
        vertice_index: int = 0,
        face_index: int = 0,
    ) -> None:
        self.vertices_count: int = vertices_count
        self.material_index: int = material_index
        self.unknown: int = unknown
        self.unknown2: int = unknown2
        self.vertice_index: int = vertice_index
        self.face_index: int = face_index

    @staticmethod
    def parse_poly_old(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["Polygon"]:
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        polys_count = int(offsets_table[table_index].size / 0x8)
        polys_list = [Polygon() for i in range(polys_count)]
        for i in range(polys_count):
            (
                vertices_count,
                unknown,
                material_index,
                unknown2,
                vertice_index,
                face_index,
            ) = struct.unpack("<BBBBHH", pmd_file.read(0x8))
            polys_list[i] = Polygon(
                vertices_count,
                material_index,
                unknown,
                unknown2,
                vertice_index,
                face_index,
            )
        pmd_file.seek(current_cursor)

        return polys_list

    @staticmethod
    def parse_poly(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["Polygon"]:
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        polys_count = int(offsets_table[table_index].size / 0x8)
        polys_list = [Polygon() for i in range(polys_count)]
        for i in range(polys_count):
            (
                vertices_count,
                material_index,
                unknown,
                unknown2,
                vertice_index,
                face_index,
            ) = struct.unpack("<BBBBHH", pmd_file.read(0x8))
            polys_list[i] = Polygon(
                vertices_count,
                material_index,
                unknown,
                unknown2,
                vertice_index,
                face_index,
            )
        pmd_file.seek(current_cursor)

        return polys_list
