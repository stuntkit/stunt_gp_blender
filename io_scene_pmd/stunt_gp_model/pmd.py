"""THis module contains most generic definition of a PMD file"""

from typing import List, Tuple, TypeVar, BinaryIO
from .filehelper import FileHelper
from .model_type import ModelType
from .vector import Vector
from .uv import UV
from .poly import Polygon
from .transform import Transform
from .mesh import Mesh
from .offsetstable import OffsetsTableElement, OffsetsTable
from .metadata import Metadata

supported_versions = [
    "1.6",
    "1.61",
    "1.62",
    # "1.7",
    # "1.82",
    "1.83",
]


class PMD:
    """Object representation of a singular PMD file"""

    # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
        self.magic = "PMD"
        self.version: str = "1.83"
        self.block_count: int = 37
        self.model_type: ModelType = ModelType.GENERIC
        self.block_0: List[Vector] = []  # Not a vert?
        # poly
        self.block_1: List[Polygon] = []
        # uv
        self.block_2: List[UV] = []

        self.block_3: List[Vector] = []
        self.block_4: List[int] = []
        self.textures: List[str] = []
        # TODO you're skipping block 6, pointers to texture names
        # Should I do that with block 8 as well?
        # Probably not as it's more like vertices and faces
        self.block_7: List[Vector] = []  # Not a vert?
        self.block_8: List[int] = []  # list of IDs to 7
        self.block_9: List[Transform] = []
        # TODO make self.lods that holds list of LODs, each holding list of meshes?
        # Do I want to store 1:1 flat file representatin here or structurized one?
        self.block_10: List[Mesh] = []
        # block 11 for now is this unholy mess
        self.block_11: Metadata = Metadata()
        # self.lods_processed = []
        self.size_12: int = 0  # ??? Number of verts in most, ??? in track

    @classmethod
    def from_file(cls, filename: str) -> "PMD":
        with open(filename, "rb") as pmd_file:  # skipcq: PTC-W6004
            pmd: PMD = PMD()

            pmd.magic, pmd.version, pmd.model_type, pmd.block_count = pmd.parse_header(
                pmd_file
            )

            # TODO rename from offsets to something more meaningful, as it also contains sizes
            offsets_table = OffsetsTable.load_table(pmd_file, pmd.block_count)

            # load all blocks
            # block 0
            pmd.block_0 = []
            if pmd.version in ["1.6", "1.61", "1.62"]:
                pmd.block_0 = Vector.parse_vector3(pmd_file, offsets_table, 0)
            else:
                pmd.block_0 = Vector.parse_vector4(pmd_file, offsets_table, 0)

            # block 1
            pmd.block_1 = Polygon.parse_poly(pmd_file, offsets_table, 1)

            # block 2
            pmd.block_2 = UV.parse_uv(pmd_file, offsets_table, 2)

            pmd.block_3 = []
            if pmd.version in ["1.6", "1.61", "1.62"]:
                pmd.block_3 = Vector.parse_vector3_todo(pmd_file, offsets_table, 3)
            else:
                pmd.block_3 = Vector.parse_vector4(pmd_file, offsets_table, 3)

            # block 4
            # TODO together with 8, load_indices()
            pmd.block_4 = pmd.__load_faces(pmd_file, offsets_table, 4)

            # blocks 5 & 6
            pmd.textures = pmd.__load_textures(
                pmd_file, offsets_table, 6, pmd.block_count
            )

            # blocks 7 & 8
            pmd.block_7 = []
            if pmd.version in ["1.6", "1.61", "1.62"]:
                pmd.block_7 = Vector.parse_vector3(pmd_file, offsets_table, 7)
            else:
                pmd.block_7 = Vector.parse_vector4(pmd_file, offsets_table, 7)
            pmd.block_8 = pmd.__load_eight(pmd_file, offsets_table, 8, pmd.block_count)

            # block 11
            if pmd.version in ["1.6", "1.61", "1.62", "1.7"]:
                pmd.block_11 = Metadata.parse_metadata_1_60(pmd_file, offsets_table, 11)
            else:
                pmd.block_11 = Metadata.parse_metadata_1_80(pmd_file, offsets_table, 11)

            # block 9
            if pmd.version in ["1.6", "1.61", "1.62", "1.7"]:
                pmd.block_9 = Transform.parse_transforms_1_60(
                    pmd_file, offsets_table, 9
                )
            elif pmd.version in ["1.82"]:
                pmd.block_9 = Transform.parse_transforms_1_82(
                    pmd_file, offsets_table, 9
                )
            else:
                pmd.block_9 = Transform.parse_transforms_1_83(
                    pmd_file, offsets_table, 9
                )

            # block 10
            if pmd.version in ["1.6", "1.61", "1.62", "1.7"]:
                pmd.block_10 = Mesh.parse_meshes_1_60(pmd_file, offsets_table, 10)
            elif pmd.version in ["1.82"]:
                pmd.block_10 = Mesh.parse_meshes_1_82(pmd_file, offsets_table, 10)
            else:
                pmd.block_10 = Mesh.parse_meshes_1_83(pmd_file, offsets_table, 10)

            # if pmd.model_type == ModelType.TRACK:

            return pmd

    @staticmethod
    def parse_header(pmd_file: BinaryIO) -> Tuple[str, str, ModelType, int]:
        current_cursor = pmd_file.tell()
        pmd_file.seek(0)
        # read PMD VX.XX string, and strip trailing \0
        magic = pmd_file.read(0x18).decode("ascii")
        version = magic[5:9].strip("\0")
        if version not in supported_versions:
            raise Exception(f"{version} is not supported")
        model_type = ModelType(FileHelper.read_uint(pmd_file))
        pmd_file.seek(current_cursor)

        # 1.6X series had only 32 blocks, 1.7X & 1.8X have 37 blocks, some of them are unused
        block_count = 37
        if version in ["1.6", "1.61", "1.62"]:
            block_count = 32

        return (magic, version, model_type, block_count)

    @staticmethod
    def __load_faces(
        pmd_file: BinaryIO, offsets_table: OffsetsTable, table_index: int
    ) -> list[int]:
        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        faces_count = int(offsets_table[table_index].size / 2)
        faces_list = [0 for i in range(faces_count)]
        for i in range(faces_count):
            face = FileHelper.read_ushort(pmd_file)
            faces_list[i] = face

        pmd_file.seek(current_cursor)

        return faces_list

    @staticmethod
    def __load_textures(
        pmd_file: BinaryIO,
        offsets_table: OffsetsTable,
        table_index: int,
        block_count: int,
    ) -> list[str]:

        address_offset = 32 + (2 * 4 * block_count)

        current_cursor = pmd_file.tell()
        pmd_file.seek(offsets_table[table_index].offset)
        textures_count = int(offsets_table[table_index].size / 4) - 1
        textures_list = ["" for i in range(textures_count)]
        for i in range(textures_count):
            offset = FileHelper.read_uint(pmd_file)
            tmp_cursor = pmd_file.tell()
            pmd_file.seek(offset + address_offset)
            texture_name = b""
            while True:
                c = pmd_file.read(1)
                if c == b"\0":
                    break
                texture_name += c
            textures_list[i] = texture_name.decode("ascii")
            pmd_file.seek(tmp_cursor)

        pmd_file.seek(current_cursor)

        return textures_list

    @staticmethod
    def __load_eight(
        pmd_file: BinaryIO,
        offsets_table: OffsetsTable,
        table_index: int,
        block_count: int,
    ) -> list[int]:
        address_offset = 32 + (2 * 4 * block_count)

        current_cursor = pmd_file.tell()
        sevens_number = int(offsets_table[table_index].size / 4)
        block_8 = [0 for i in range(sevens_number)]
        for i in range(sevens_number):
            pmd_file.seek(offsets_table[table_index].offset + (4 * i))
            block_8[i] = FileHelper.read_uint(pmd_file) + address_offset
        pmd_file.seek(current_cursor)

        return block_8
