"""This module store everything connected to a sigular mesh transform"""

import struct
from typing import BinaryIO

from .offsetstable import OffsetsTable

# class Transform1_60:
#     """A singular mesh transform"""

#     # 3x4
#     # pylint: disable=too-many-arguments
#     def __init__(self, matrix, uk, uk1):
#         self.matrix = matrix  #: mathutils.Matrix = matrix
#         self.unknown: int = uk
#         self.unknown1: int = uk1


# class Transform1_82:
#     """A singular mesh transform"""

#     # 4x4
#     # pylint: disable=too-many-arguments
#     def __init__(self, matrix, uk, uk1):
#         self.matrix = matrix  #: mathutils.Matrix = matrix
#         self.unknown: int = uk
#         self.unknown1: int = uk1


class Transform:  # 1_83:
    """A singular mesh transform"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        matrix: list[list[float]],
        uk: int = 0,
        uk1: int = 0,
        uk2: int = 0,
        uk3: int = 0,
    ):
        self.matrix = matrix  #: mathutils.Matrix = matrix
        self.unknown: int = uk
        self.unknown1: int = uk1
        self.unknown2: int = uk2
        self.unknown3: int = uk3

    # TODO
    @staticmethod
    def parse_transform_1_60(
        pmd_file: BinaryIO,
        offsets_table: OffsetsTable,
        table_index: int,
        transform_index: int,
    ) -> "Transform":
        # RRR-
        # RRR-
        # RRR-
        # SSS-
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset + (0x38 * transform_index))
        matrix_data: list[list[float]] = [[0.0, 0.0, 0.0, 0.0] for j in range(4)]
        for j in range(4):
            matrix_data[j] = [*struct.unpack("<3f", pmd_file.read(0xC)), 1.0]

        unknowns = struct.unpack("<2L", pmd_file.read(0x8))
        transform = Transform(matrix_data, *unknowns)
        pmd_file.seek(current_cursor)
        return transform

    @staticmethod
    def parse_transform_1_82(
        pmd_file: BinaryIO,
        offsets_table: OffsetsTable,
        table_index: int,
        transform_index: int,
    ) -> "Transform":
        # TOD check if correct
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset + (0x48 * transform_index))
        matrix_data: list[list[float]] = [[0.0, 0.0, 0.0, 0.0] for j in range(4)]
        for j in range(4):
            matrix_data[j] = [*struct.unpack("<4f", pmd_file.read(0x10))]
        unknowns = struct.unpack("<2L", pmd_file.read(0x8))
        transform = Transform(matrix_data, *unknowns)
        pmd_file.seek(current_cursor)
        return transform

    @staticmethod
    def parse_transform_1_83(
        pmd_file: BinaryIO,
        offsets_table: OffsetsTable,
        table_index: int,
        transform_index: int,
    ) -> "Transform":
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset + (0x50 * transform_index))
        matrix_data: list[list[float]] = [[0.0, 0.0, 0.0, 0.0] for j in range(4)]
        for j in range(4):
            matrix_data[j] = [*struct.unpack("<4f", pmd_file.read(0x10))]
        unknowns = struct.unpack("<4L", pmd_file.read(0x10))
        transform = Transform(matrix_data, *unknowns)
        pmd_file.seek(current_cursor)
        return transform

    @staticmethod
    def parse_transforms_1_60(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["Transform"]:
        transforms: list["Transform"] = []
        transforms_count = int(offsets_table[table_index].size / 56)
        for i in range(transforms_count):
            transforms.append(
                Transform.parse_transform_1_60(pmd_file, offsets_table, table_index, i)
            )
        return transforms

    @staticmethod
    def parse_transforms_1_82(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["Transform"]:
        transforms: list["Transform"] = []
        transforms_count = int(offsets_table[table_index].size / 72)
        for i in range(transforms_count):
            transforms.append(
                Transform.parse_transform_1_82(pmd_file, offsets_table, table_index, i)
            )
        return transforms

    @staticmethod
    def parse_transforms_1_83(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list["Transform"]:
        transforms: list["Transform"] = []
        transforms_count = int(offsets_table[table_index].size / 80)
        for i in range(transforms_count):
            transforms.append(
                Transform.parse_transform_1_83(pmd_file, offsets_table, table_index, i)
            )
        return transforms
