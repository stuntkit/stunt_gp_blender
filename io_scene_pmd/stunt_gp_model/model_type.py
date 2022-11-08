"""This module defines model types that can be stored in a PMD file"""
from enum import Enum


class ModelType(Enum):
    """type of a model stored in the PMD"""

    GENERIC = 0
    TRACK = 1
    CAR = 2
