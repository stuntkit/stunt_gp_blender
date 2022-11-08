#!/usr/bin/env python3
"""literally a test file"""

from stunt_gp_model import PMD

FILEPATH = "/dane/repos/stunt_gp/stunt_gp_blender/meshdata/car2.PMD"
# FILEPATH = "/home/halamix2/repos/stunt_gp/models_collected/1_60/CAR9SHADOW.PMD"
file = pmd = PMD.from_file(FILEPATH)

print("")
