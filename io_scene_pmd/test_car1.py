#!/usr/bin/env python3
"""literally a test file"""

from stunt_gp_model import PMD, OffsetsTable

FILEPATH = "/home/halamix2/repos/stunt_gp/models_collected/1_60/CAR1.PMD"
# FILEPATH = "/home/halamix2/repos/stunt_gp/models_collected/1_60/CAR9SHADOW.PMD"
pmd = PMD.from_file(FILEPATH)

pmd_file = open(FILEPATH, "rb")

offsets_table = OffsetsTable.load_table(pmd_file, pmd.block_count)

i = 0
for meshblock in pmd.block_10:
    print("mesh", i)
    i += 1
    print(
        "poly\t",
        meshblock.polys_count,
        meshblock.polys_start_index,
        (offsets_table[1].size // 0x8),
    )
    print(
        "uv\t",
        meshblock.uvs_count,
        meshblock.uvs_start_index,
        (offsets_table[2].size // 0x10),
    )
    print(
        "vert\t",
        meshblock.verts_count,
        meshblock.verts_start_index,
        (offsets_table[3].size // 0x10),
    )

pmd_file.close()
# print("7:", len(pmd.block_7))
# print("8:", len(pmd.block_8))
# print("ind,lod,uk1,uk2,uk3,uk4,uk5,uk6,uk7,uk8,uk9,uk10,uk11,uk12,uk_ind1,uk_ind2")
# for i, mesh in enumerate(pmd.block_10):
#     lod = i // 25
#     # print(mesh.unknown_index) too long
#     # print(
#     #    f"{i-25*lod},{lod},{mesh.unknown},{mesh.unknown2},{mesh.unknown3},{mesh.unknown4},{mesh.unknown5},{mesh.unknown6},{mesh.unknown7},{mesh.unknown8},{mesh.unknown9},{mesh.unknown10},{mesh.unknown11},{mesh.unknown12},{mesh.uk_index},{mesh.uk_index2}"
#     # )
