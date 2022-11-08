"""This module contains various generic useful functions"""
# TODO name this helper or utils?
from typing import BinaryIO
import struct


class FileHelper:
    """this class contains methods that will help read binary data into various data types"""

    @staticmethod
    def read_float(file_obj: BinaryIO) -> float:
        """reads 4 bytes as float"""
        # TODO can this be done better with mypy not complaining?
        data: float = struct.unpack("<f", file_obj.read(4))[0]
        return data

    @staticmethod
    def read_ubyte(file_obj: BinaryIO) -> int:
        """reads 1 byte as unsigned byte"""
        data: int = struct.unpack("<B", file_obj.read(1))[0]
        return data

    @staticmethod
    def read_ushort(file_obj: BinaryIO) -> int:
        """reads 2 bytes as unsigned short"""
        data: int = struct.unpack("<H", file_obj.read(2))[0]
        return data

    @staticmethod
    def read_uint(file_obj: BinaryIO) -> int:
        """reads 4 bytes as unsigned int"""
        data: int = struct.unpack("<L", file_obj.read(4))[0]
        return data

    # TODO read lists, useful for transforms, eight

    # @staticmethod
    # def get_data_block(pmd_file, offset: int, size: int, in_place=False):
    #     """gets singular data block from whole pmd file, based on the offsets table"""
    #     current_cursor = pmd_file.tell()
    #     pmd_file.seek(offset)
    #     data_block = pmd_file.read(size)
    #     if not in_place:
    #         pmd_file.seek(current_cursor)
    #     return data_block
