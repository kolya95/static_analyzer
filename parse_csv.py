__author__ = 'kolya'
import csv
from generate_tables import types_array
names = [str(type(types_array[j]))[8:-2] for j in range(len(types_array))]

description = {name:{} for name in names}


type_IDS ={
    'NoneType': 0,
    'bool' : 1,
    'int' : 2,
    'float' : 3,
    'str' : 4,
    'list' : 5,
    'dict' : 6,
    'tuple' : 7,
    'set' : 8,
    'bytes' : 9,
    'bytearray' : 10,
    'range' : 11,
    'frozenset' : 12,
    'contextmanager' : 13,
    'memoryview' : 14
}


for name in names:
    f = open('binary/'+name+'.csv')
    f_reader = csv.DictReader(f, delimiter=';')
    # methods = f_reader.readline()
    # for i in range(len(methods)):
    for j in f_reader:
        for key in j.keys():
            if j[key].split(':')[1] == 'NotImplementedType':
                continue
            # print(j[key].split(':'))
            # print(type_IDS[j[key].split(':')[1]])
            # print(type_IDS[j[key].split(':')[0]])

            try:
                 description[name][key].append({type_IDS[j[key].split(':')[0]]:type_IDS[j[key].split(':')[1]]})
            except:
                 description[name][key] = [({type_IDS[j[key].split(':')[0]]:type_IDS[j[key].split(':')[1]]})]

print(description)