"""This module stores vertex info"""

from typing import Tuple, List, BinaryIO
import struct
from .offsetstable import OffsetsTable


class Vector:
    """The vertex class"""

    def __init__(self, x: float, y: float, z: float, w: float) -> None:
        # pylint: disable=invalid-name
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.w: float = w
        # pylint: enable=invalid-name

    def get_coords_blender(self, scale: float = 1.0) -> Tuple[float, float, float]:
        """return the data in a format expected by Blender"""
        # TODO don't swicth z & y here, flip everything on a higher lever
        # also scale
        return (
            (self.x / self.w) * scale,
            (self.z / self.w) * scale,
            (self.y / self.w) * scale,
        )

    # TODO neat str and repr
    def __str__(self) -> str:
        return f"{self.x}, {self.y}, {self.z}"

    @staticmethod
    def parse_vector3(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> List["Vector"]:
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        vertices_count = int(offsets_table[table_index].size / 0xC)
        vertices_list = [Vector(0, 0, 0, 0) for i in range(vertices_count)]
        for i in range(vertices_count):
            x, y, z = struct.unpack("<fff", pmd_file.read(0xC))
            vertices_list[i] = Vector(x, y, z, 1.0)
        pmd_file.seek(current_cursor)
        return vertices_list

    @staticmethod
    def parse_vector4(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> List["Vector"]:
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        vertices_count = int(offsets_table[table_index].size / 0x10)
        vertices_list = [Vector(0, 0, 0, 0) for i in range(vertices_count)]
        for i in range(vertices_count):
            x, y, z, w = struct.unpack("<ffff", pmd_file.read(0x10))
            vertices_list[i] = Vector(x, y, z, w)
        pmd_file.seek(current_cursor)
        return vertices_list
