#!/usr/bin/python3
# coding=utf-8

# import os
# import sys

# files
# from pathlib import Path

from glob import glob

from stunt_gp_model import PMD


# binary
import struct


def analysis(f):
    pmd = PMD.from_file(f)
    print(f)
    for i, poly in enumerate(pmd.block_1):
        known = False
        if (
            (poly.unknown == 255 and poly.unknown2 == 32)
            or (poly.unknown == 143 and poly.unknown2 == 200)
            or (poly.unknown == 255 and poly.unknown2 == 160)
        ):
            known = True
        if not known:
            print(f"{poly.unknown}, {poly.unknown2}")
    # for i, mesh in enumerate(pmd.block_10):
    #     if mesh.unknown2 + mesh.uk_index2 > len(pmd.block_8):
    #         print(
    #             f"fuckup, {mesh.unknown2}+{mesh.uk_index2}={mesh.unknown2+mesh.uk_index2}, expected {len(pmd.block_8)} on {i}"
    #         )


def main():
    files = glob("car1sh.PMD")
    files = glob("/dane/repos/stunt_gp/stunt_gp_blender/meshdata/car2.PMD")
    files.sort()
    for f in files:
        print(f)
        try:
            analysis(f)
        except:
            pass


if __name__ == "__main__":
    main()
