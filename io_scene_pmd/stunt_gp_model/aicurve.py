"""This module stores AI curve info"""

from typing import List, BinaryIO
import struct
from .offsetstable import OffsetsTable


class AICurve:
    """The AI curve class"""

    def __init__(
        self,
        id: int = 0,
        vertice_index: int = 0,
        length: int = 0,
        un: int = 0,
        un1: int = 0,
        un2: int = 0,
        un3: float = 0,
    ) -> None:
        self.id: int = id
        self.vertice_index: int = vertice_index
        self.length: int = length
        self.un: int = un
        self.un1: int = un1
        self.un2: int = un2
        self.un3: float = un3

    @staticmethod
    def parse_aicurve(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> List["AICurve"]:
        """Parses 1.83 AICurvve definiton"""
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        aicurve_count = int(offsets_table[table_index].size / 0x1C)
        aicurve_list = [AICurve() for i in range(aicurve_count)]

        for i in range(aicurve_count):
            data = struct.unpack("<6If", pmd_file.read(0x1C))
            aicurve_list[i] = AICurve(*data)

        pmd_file.seek(current_cursor)
        return aicurve_list
