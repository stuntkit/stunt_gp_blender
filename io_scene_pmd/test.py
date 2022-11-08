#!/usr/bin/env python3
"""literally a test file"""

from stunt_gp_model import PMD

FILEPATH = "/dane/repos/stunt_gp/stunt_gp_blender/meshdata/car2.PMD"
# FILEPATH = "/home/halamix2/repos/stunt_gp/models_collected/1_60/CAR9SHADOW.PMD"
file = pmd = PMD.from_file(FILEPATH)

# print("7:", len(pmd.block_7))
# print("8:", len(pmd.block_8))
# print("ind,lod,uk1,uk2,uk3,uk4,uk5,uk6,uk7,uk8,uk9,uk10,uk11,uk12,uk_ind1,uk_ind2")
# for i, mesh in enumerate(pmd.block_10):
#     lod = i // 25
#     # print(mesh.unknown_index) too long
#     # print(
#     #    f"{i-25*lod},{lod},{mesh.unknown},{mesh.unknown2},{mesh.unknown3},{mesh.unknown4},{mesh.unknown5},{mesh.unknown6},{mesh.unknown7},{mesh.unknown8},{mesh.unknown9},{mesh.unknown10},{mesh.unknown11},{mesh.unknown12},{mesh.uk_index},{mesh.uk_index2}"
#     # )
