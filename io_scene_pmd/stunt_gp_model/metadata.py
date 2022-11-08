"""This module contains model metdata information"""

import struct
from typing import BinaryIO

from .offsetstable import OffsetsTable
from .filehelper import FileHelper


class Metadata:  # 1_80:
    """metadata in simplified format"""

    def __init__(self, meshes_per_lod: int = 25, lods: list[int] = []) -> None:
        self.meshes_per_lod = meshes_per_lod

        # TODO thee unknowns

        # indices where each LOD starts
        self.lods = lods

    @property
    def number_of_lods(self) -> int:
        return len(self.lods)

    @staticmethod
    def parse_metadata_1_60(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> "Metadata":
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        # meshes_per_lod = struct.unpack("<BBBHHH", pmd_file.read(0xBC))
        # metadata: Metadata = Metadata(meshes_per_lod)
        pmd_file.seek(current_cursor)
        raise Exception("Unimplemented")
        # return metadata

    @staticmethod
    def parse_metadata_1_80(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> "Metadata":
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset + 0x24)
        meshes_per_lod = FileHelper.read_uint(pmd_file)
        pmd_file.seek(offsets_table[table_index].offset + 0x48)
        (
            index0,
            index1,
            index2,
            index3,
            lod_count,
        ) = struct.unpack("<5L", pmd_file.read(0x14))

        lods = [index0, index1, index2, index3]
        lods = lods[: lod_count + 1]
        metadata: Metadata = Metadata(meshes_per_lod, lods)
        pmd_file.seek(current_cursor)
        return metadata
