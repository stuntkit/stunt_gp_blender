"""This module stores definition of UV data"""


from typing import BinaryIO
from .offsetstable import OffsetsTable
import struct


class UV:
    """Singular uv coordinates and data"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        u: float = 0.0,
        v: float = 0.0,
        vertex_id: int = 0,
        material_index: int = 0,
        unknown: int = 0,
    ) -> None:
        # pylint: disable=invalid-name
        self.u: float = u
        self.v: float = v
        # pylint: enable=invalid-name

        self.vertex_id: int = vertex_id

        # TODO check if I'm correct on that
        self.material_index: int = material_index

        # Color?
        self.unknown: int = unknown

    @staticmethod
    def parse_uv(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["UV"]:
        """loads data into UV class"""
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        uvs_count = int(offsets_table[table_index].size / 0x10)
        uvs_list = [UV() for i in range(uvs_count)]
        for i in range(uvs_count):
            (
                u,
                v,
                vertex_id,
                material_index,
                unknown,
            ) = struct.unpack("<ffHHL", pmd_file.read(0x10))
            uvs_list[i] = UV(u, v, vertex_id, material_index, unknown)
        pmd_file.seek(current_cursor)

        return uvs_list
