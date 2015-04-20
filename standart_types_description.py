__author__ = 'kolya'
from enum import Enum
from types_analysis import *

class TypeIndex(Enum):
    none = 0
    bool = 1
    int = 2
    float = 3
    string = 4
    list = 5
    dict = 6
    tuple = 7
    set = 8
    bytes = 9
    bytearray = 10
    range = 11
    frozenset = 12
    contextmanager = 13
    memoryview = 14


import inspect