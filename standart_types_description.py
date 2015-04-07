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


int_methods = [
    MethodDescription('__abs__', None, TypeIndex.int.value),
    MethodDescription('__add__', [(None,  TypeIndex.int.value), (None,  TypeIndex.bool.value)], TypeIndex.int.value),
    MethodDescription('__and__', [(None,  TypeIndex.int.value), (None,  TypeIndex.bool.value)], TypeIndex.int.value),
    MethodDescription('__bool__', None, TypeIndex.bool.value),
    MethodDescription('__ceil__', None, TypeIndex.int.value),
    MethodDescription('__class__', [(None,  TypeIndex.int.value), (None,  TypeIndex.bool.value), (None, TypeIndex.string.value)], TypeIndex.int.value),
    MethodDescription('__delattr__', [(None, TypeIndex.string.value)], None),  #????
    MethodDescription('__dir__', None, TypeIndex.list.value),
    MethodDescription('__divmod__', [(None,  TypeIndex.int.value), (None,  TypeIndex.bool.value)], TypeIndex.tuple.value),
    # __doc__ -- не метод, описывать надо?
    MethodDescription('__eq__', [(None,  TypeIndex.int.value), (None,  TypeIndex.bool.value)], TypeIndex.bool.value),
    MethodDescription('__float__', None, TypeIndex.float.value),
    MethodDescription('__floor__', None, TypeIndex.int.value),



]
int_description = TypeTableElement("int", int_methods)


