"""This module stores list of blocks defined in the PMD file header"""

from typing import List, TypeVar, Iterable, Tuple, BinaryIO
from .filehelper import FileHelper


class OffsetsTableElement:
    """singular element of the list"""

    def __init__(self, offset: int = 0, size: int = 0):
        self.offset = offset
        self.size = size

    def __str__(self) -> str:
        return f"{hex(self.offset)}, {hex(self.size)}"

    def __repr__(self) -> str:
        return f"[{hex(self.offset)}, {hex(self.size)}]"

    # TODO add serialization to two lists, and deserialization


class OffsetsTable(list[OffsetsTableElement]):
    def __init__(self, *args: OffsetsTableElement):
        super().__init__(args)

    @classmethod
    def load_table(cls, pmd_file: BinaryIO, block_count: int = 0) -> "OffsetsTable":
        # load absolute offsets and sizes foe each block. Blocks with 0 offset are invalid
        # TODO this is ugly
        current_cursor = pmd_file.tell()
        pmd_file.seek(0x20)
        offsets_table: "OffsetsTable" = OffsetsTable(
            *[OffsetsTableElement() for i in range(block_count)]
        )

        # header + 2 * int * block_count
        address_offset = 32 + (2 * 4 * block_count)

        for i, off in enumerate(offsets_table):
            off.offset = FileHelper.read_uint(pmd_file)
            # Block 11 is the only one that should have relative offset set to 0
            if (i == 11) or (off.offset > 0):
                off.offset += address_offset

        for off in offsets_table:
            off.size = FileHelper.read_uint(pmd_file)
        pmd_file.seek(current_cursor)

        return offsets_table

    @staticmethod
    def get_offsets_table(offsets_table: List[OffsetsTableElement]) -> List[int]:
        address_offset = 32 + (2 * 4 * len(offsets_table))
        return [i.offset - address_offset for i in offsets_table]

    @staticmethod
    def get_sizes_table(offsets_table: List[OffsetsTableElement]) -> List[int]:
        return [i.size for i in offsets_table]
