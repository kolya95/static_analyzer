__author__ = 'kolya'

class MethodDescription:
    def __init__(self, name=None, return_type=None, args=None):
        self.name = name
        self.args = args
        self.return_type = return_type

class TypeTableElement:
    def __init__(self, name=None, methods_description=None, base_classes_set=None, key_value_types=None):
        self.name = name
        self.bc = base_classes_set
        self.md = methods_description
        self.kv_t = key_value_types



