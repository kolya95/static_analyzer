__author__ = 'kolya'

from inspect import getmembers as gm
types_array = [1, 1.0, "1", [1], (1,)]


print_table = {str(type(types_array[j]))[8:-2]:{} for j in range(len(types_array))}


for i in range(len(types_array)):
    for method in gm(types_array[i]):
        s = []
        for j in range(len(types_array)):
            try:
                s +=[ {str(type(types_array[j]))[8:-2]:( str(type(method[1]( types_array[j] )))[8:-2] ) }]
            except:
                pass
        if len(s) == len(types_array):
            print_table[str(type(types_array[i]))[8:-2]][method[0]] = s
print(print_table)

import csv, os

try:
    os.mkdir('binary')
except:
    pass

for key in print_table.keys():
    f = open('binary/'+key+'.csv', 'w')
    f_writer = csv.writer(f, delimiter=';')
    f_writer.writerow(list( print_table[key].keys()))
    for i in range(len(types_array)):
        f_writer.writerow([list(print_table[key][method][i].keys())[0]+':'+(print_table[key][method][i][list(print_table[key][method][i].keys())[0]]) for method in print_table[key].keys()])
    f.close()