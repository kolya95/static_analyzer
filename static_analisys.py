""" static analyzer for python 3"""
# -*- coding: utf-8 -*-
import keyword
import token
import parser
import importlib
import inspect

import analizer_instance


from parse_csv import type_IDS
class Name:
    """ super class for all names (variables, functions etc)
    """
    def __init__(self, name, visible_names=[]):
        self.name = name
        self.visible_names = visible_names


class Variable(Name):
    """ class for variables
    """
    def __init__(self, name, typeID=type_IDS['UNDEFINED']):
        Name.__init__(self, name)
        self.initialized = True
        self.type = typeID

    def __eq__(self, other):
        if self.name == other.name:
            return True


class Callable(Name):
    """ base class for callable objects (functions, methods etc.)
        body -- tree of function body
        visible names -- names, that visible in this scope
        global names -- names, that defined as global or in global scope
        local names -- names, that defined in the function body
        args -- tree of arguments
        return type -- type, that will be returned
    """
    def __init__(self, name, visible_names=[], global_names=[], local_names=[], body=[], args=[], return_type=None):
        Name.__init__(self, name)
        self.body = []
        self.body += body

        self.args = []
        self.args += args

        self.return_type = []
        self.return_type += [return_type]

        self.local_names = []
        self.local_names += local_names

        self.global_names = []
        self.global_names += global_names

        self.visible_names = []
        self.visible_names += visible_names

        self.global_used = []

        self.as_global = []

    def do_all(self, st, visible):
        self.parse(st, visible)
        self.local_variable()
        for s in self.local_names:
            if isinstance(s, Function) and len(s.body) >= 1:
                s.do_all(s.body, self.local_names)
                s.local_variable()

    def is_as_global(self,v):
        for sym in self.as_global:
            if sym.name == v.name:
                return True
        return False

    def parse_args(self, st, local):
        if st[0] in NON_TERMINAL:
            if st[0] == 265 and not self.is_as_global(Variable(st[1][1])):
                self.local_names.append(Variable(st[1][1]))
            else:
                for j in range(1, len(st)):
                    self.parse_args(st[j], local)
        else:
            return

    def local_variable(self):
            for used in self.global_used:
                for var in self.local_names:
                    if used[0].name == var.name and (not self.is_as_global(var)):
                        err = analizer_instance.Error(used[1]-1, used[2], len(used.name), "Undefined local variable")
                        # err = MyError(used[1], used[2], "error, use local variable before defining" + " line " + str(used[1]) + " position " + str(used[2]))
                        if err not in ERROR_LIST:
                            ERROR_LIST.append(err)

    def parse(self, st, visible, type_var=type_IDS['UNDEFINED']):
        """ parses function body"""



        def parse_right_part(st):
            if st[0] in NON_TERMINAL:
                if (st[0] == 319) and len(st) > 2 and st[1][1][0] == token.NAME and st[2][0] != 322:
                    var_name = st[1][1][1]

                    if not isinstance(st[2], int):
                        for name in st[2]:
                            if not isinstance(name, int):
                                var_name += name[1]

                    if not is_local_identified(Name(var_name)) and not is_global_identified(Name(var_name)):
                        err = analizer_instance.Error(st[1][1][2]-1, st[1][1][3], len(var_name), "Undefined name")
                        # err = MyError(st[1][1][2], st[1][1][3], "error, undefined variable" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                        if err not in ERROR_LIST:
                            ERROR_LIST.append(err)
                elif (st[0] == 320) and (st[1][0] == token.NAME) and (not is_local_identified(Name(st[1][1]))) and (is_global_identified(Name(st[1][1]))):
                    self.global_used.append([Variable(st[1][1]), st[1][2], st[1][3]])
                elif (st[0] == 320) and (st[1][0] == token.NAME) and (not is_local_identified(Name(st[1][1]))) and (not is_global_identified(Name(st[1][1]))):
                    err = analizer_instance.Error(st[1][2]-1, st[1][3], len(st[1][1]), "Undefined name")
                    # err = MyError(st[1][2], st[1][3], "error, undefined variable" + " line " + str(st[1][2]) + " position " + str(st[1][3]))
                    if err not in ERROR_LIST:
                        ERROR_LIST.append(err)
                elif (st[0] == 320) and len(st)>2 and (st[2][0]==321):
                    parse_compound_stmt(st[2],visible)
                elif st[0] == 331 and len(st) == 4:
                    add_var(st[1], type_var)
                    parse_right_part(st[3])
                else:
                    for j in range(1,len(st)):
                        parse_right_part(st[j])

        def is_global_identified(sym):
            for s in GLOBAL_SYMBOL_LIST + self.visible_names:
                if sym.name == s.name:
                    return True
            return False

        def is_local_identified(sym):
            for s in self.local_names:
                if sym.name == s.name:
                    return True
            return False

        def var_or_call(st, st271):
            if st[0] in NON_TERMINAL:
                if st[0] == 319 and len(st) == 3 and st[2][0] == 322:
                    v_name = st[1][1][1]
                    if st[2][1][1] == '.':
                        for name in st[2]:
                            if not isinstance(name, int):
                                v_name += name[1]
                    else:
                        parse_right_part(st[2])
                    sym = Name(v_name)
                    if is_local_identified(sym):
                        for s in self.local_names:
                            if isinstance(s, Function) and s.name == sym.name and len(s.body)>=1:
                                #parse_right_part(s.args)
                                s.parse(s.body, self.visible_names + self.local_names)
                                for p in s.local_names:
                                    if isinstance(p, Function) and len(p.body)>1:
                                        p.parse(p.body, p.visible_names + self.local_names)
                                break
                    elif is_global_identified(sym):
                        for s in self.local_names:
                            if isinstance(s, Function) and s.name == sym.name and len(s.body)>=1:
                                s.parse(s.body, self.visible_names + self.local_names)
                                for p in s.local_names:
                                    if isinstance(p, Function) and len(p.body)>1:
                                        p.parse(p.body, p.visible_names + self.local_names)
                                break
                    else:
                        err = analizer_instance.Error(st[1][1][2]-1, st[1][1][3], len(sym.name), "Undefined function name")
                        # err = MyError(st[1][1][2],st[1][1][3],"error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                        if err not in ERROR_LIST:
                            ERROR_LIST.append(err)
                elif st[0] == 319 and len(st) != 3:
                    parse_right_part(st271)
                else:
                    for j in range(1,len(st)):
                        var_or_call(st[j],st271)


        def add_var(st, type_var=type_IDS['UNDEFINED']):
            if st[0] == 320 and not keyword.iskeyword(st[1][1]) and st[1][0]==token.NAME:
                if not is_local_identified(Variable(st[1][1], type_var)) and not self.is_as_global(Variable(st[1][1], type_var)):
                    self.local_names.append(Variable(st[1][1], type_var))
            elif st[0] == 319 and len(st)>2 and st[2][0] == 322:
                if not is_global_identified(Variable(st[1][1][1], type_var)) and not is_local_identified(Variable(st[1][1][1], type_var)):
                    self.local_names.append(Variable(st[1][1][1], type_var))
                parse_right_part(st[2])
            else:
                for j in range(1,len(st)):
                    if st[j][0] in NON_TERMINAL:
                        add_var(st[j], type_var)



        def parse_compound_stmt(st, visible):
            if st[0] == 262:
                self.local_names.append(Function(st[2][1], visible + self.local_names, GLOBAL_SYMBOL_LIST, [], st[5], st[3]))
                self.local_names[len(self.local_names)-1].parse_args(self.local_names[len(self.local_names)-1].args, self.local_names[len(self.local_names)-1].local_names)
                visible.append(self.local_names[len(self.local_names)-1])
            elif st[0] == 296:
                parse_right_part(st[4])
                add_var(st[2], type_var)
                self.parse(st[6], self.visible_names)
            elif st[0] == 329:
                GLOBAL_SYMBOL_LIST.append(Class(st[2][1], st))
            elif st[0] == 321 and len(st)>2 and st[2] == 333:
                add_var(st[2][2], type_var)
                parse_right_part(st[1])
                parse_right_part(st[2][4])
            elif st[0] == 294:
                for statement in st:
                    if not isinstance(statement,int) and statement[0] == 302:
                        parse_right_part(statement)
                    elif not isinstance(statement,int):
                        self.parse(statement,self.visible_names + self.local_names)
            elif st[0] == 321 and len(st) == 2:
                parse_right_part(st[1])
            else:
                self.parse(st, self.visible_names + self.local_names)

        def parse_import(st):
            if st[0] == 283:
                import_name(st[2])
            elif st[0] == 284:
                module_name = ""
                if not isinstance(st[2], int):
                    for name in st[2]:
                        if not isinstance(name, int):
                            module_name += name[1]
                try:
                    module = importlib.import_module(module_name)
                except ImportError:
                    print("Import Error, No module named " + module_name)
                    exit()
                if len(st)==5 and st[4][1] == "*":
                    syms = inspect.getmembers(module)
                    str_syms = dir(module)
                    name_as = ""
                    for sym in syms:
                        if inspect.isfunction(sym[1]):
                            GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                        elif inspect.isbuiltin(sym[1]):
                            GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                        elif inspect.ismethod(sym[1]):
                            pass
                        elif inspect.isgeneratorfunction:
                            GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                        elif inspect.isgenerator(sym[1]):
                            pass
                        elif inspect.istraceback(sym[1]):
                            pass
                        elif inspect.isframe(sym[1]):
                            pass
                        elif inspect.iscode(sym[1]):
                            pass
                        elif inspect.isroutine(sym[1]):
                            pass
                        elif inspect.isabstract(sym[1]):
                            pass
                        elif inspect.ismemberdescriptor(sym[1]):
                            pass
                        elif inspect.isdatadescriptor(sym[1]):
                            pass
                        elif inspect.isdatadescriptor(sym[1]):
                            pass
                        elif inspect.isgetsetdescriptor(sym[1]):
                            pass
                        elif inspect.ismemberdescriptor(sym[1]):
                            pass
                        elif inspect.isclass(sym[1]):
                            GLOBAL_SYMBOL_LIST.append(Class(sym[0]))
                        else:
                            print(sym[0])
                else:
                    for counter in range(len(st[4])):
                        if not isinstance(st[4][counter],int) and st[4][counter][0] == 285:
                            import_from(st[4][counter], module)

        def import_name(s1):
            if s1[0] in NON_TERMINAL:
                if s1[0] in NON_TERMINAL and s1[0] == 286:
                    dot_name = ""
                    module_name = ""
                    for name in s1[1]:
                        if not isinstance(name, int):
                            module_name += name[1]
                    if len(s1) == 2:
                        dot_name = module_name
                    elif len(s1) == 4:
                        dot_name = s1[3][1]
                    try:
                        module = importlib.import_module(module_name)
                    except ImportError:
                        print("Import Error, No module named " + module_name)
                        exit()
                    new_module = Module(module_name)
                    new_module.SYMBOL_LIST = []
                    syms = inspect.getmembers(module)
                    for sym in syms:
                        if inspect.isfunction(sym[1]):
                            #new_module.SYMBOL_LIST.append(Function(dot_name+'.' + sym[0]))
                            new_module.SYMBOL_LIST.append(Function(sym[0]))
                        elif inspect.isbuiltin(sym[1]):
                            new_module.SYMBOL_LIST.append(Function(sym[0]))
                        elif inspect.ismethod(sym[1]):
                            pass
                        elif inspect.isgeneratorfunction:
                            new_module.SYMBOL_LIST.append(Function(sym[0]))
                        elif inspect.isgenerator(sym[1]):
                            pass
                        elif inspect.istraceback(sym[1]):
                            pass
                        elif inspect.isframe(sym[1]):
                            pass
                        elif inspect.iscode(sym[1]):
                            pass
                        elif inspect.isroutine(sym[1]):
                            pass
                        elif inspect.isabstract(sym[1]):
                            pass
                        elif inspect.ismemberdescriptor(sym[1]):
                            pass
                        elif inspect.isdatadescriptor(sym[1]):
                            pass
                        elif inspect.isdatadescriptor(sym[1]):
                            pass
                        elif inspect.isgetsetdescriptor(sym[1]):
                            pass
                        elif inspect.ismemberdescriptor(sym[1]):
                            pass
                        elif inspect.isclass(sym[1]):
                            new_module.SYMBOL_LIST.append(Class(sym[0], [], []))
                        else:
                            print(sym[0])
                        self.local_names.append(new_module)
                else:
                    for j in range(1,len(s1)):
                        import_name(s1[j])

        def import_from(s1, module):
            syms = inspect.getmembers(module)
            str_syms = dir(module)
            name_as = ""
            if len(s1) == 4:
                name_as = s1[3][1]

            if not (s1[1][1] in str_syms):
                print("import error")
                exit()
            else:
                for sym in syms:
                    if sym[0] == s1[1][1]:
                        if inspect.isfunction(sym[1]):
                            if len(s1) == 4:
                                self.local_names.append(Function(name_as))
                            else:
                                self.local_names.append(Function(sym[0]))
                        elif inspect.isbuiltin(sym[1]):
                            if len(s1) == 4:
                                self.local_names.append(Function(name_as))
                            else:
                                self.local_names.append(Function(sym[0]))
                        elif inspect.ismethod(sym[1]):
                            pass
                        elif inspect.isgeneratorfunction:
                            if len(s1) == 4:
                                self.local_names.append(Function(name_as))
                            else:
                                self.local_names.append(Function(sym[0]))
                        elif inspect.isgenerator(sym[1]):
                            pass
                        elif inspect.istraceback(sym[1]):
                            pass
                        elif inspect.isframe(sym[1]):
                            pass
                        elif inspect.iscode(sym[1]):
                            pass
                        elif inspect.isroutine(sym[1]):
                            pass
                        elif inspect.isabstract(sym[1]):
                            pass
                        elif inspect.ismemberdescriptor(sym[1]):
                            pass
                        elif inspect.isdatadescriptor(sym[1]):
                            pass
                        elif inspect.isdatadescriptor(sym[1]):
                            pass
                        elif inspect.isgetsetdescriptor(sym[1]):
                            pass
                        elif inspect.ismemberdescriptor(sym[1]):
                            pass
                        elif inspect.isclass(sym[1]):
                            if len(s1) == 4:
                                self.local_names.append(Class(name_as))
                            else:
                                self.local_names.append(Class(sym[0]))
                        else:
                            print(sym[0])




        if len(st) > 0 and st[0] in NON_TERMINAL:
            if st[0] == 271 and len(st) == 4 and st[2][0] != 273:
                parse_right_part(st[3])
                r = parse_type_of_arith_expr(st[3], GLOBAL_SYMBOL_LIST + self.local_names)
                self.parse(st[1], visible, r)
            elif st[0] == 323:
                parse_right_part(st)
            elif st[0] == 271 and len(st) == 4 and st[2][0] == 273:
                parse_right_part(st[1])
                add_var(st[1], type_var)
                parse_right_part(st[3])
            elif st[0] == 271 and len(st) == 2:
                var_or_call(st,st)
            elif st[0] == 320 and not keyword.iskeyword(st[1][1]) and st[1][0] == token.NAME and not is_local_identified(Variable(st[1][1])):
                self.local_names.append(Variable(st[1][1], type_var))
                #print(st[1][1])
            elif st[0] == 293:
                parse_compound_stmt(st[1], visible)
            elif st[0] == 290:
                for j in range(2, len(st)):
                    if st[j][0] == 1:
                        globvar = Variable(st[j][1])
                        #globvar.initialized = False
                        self.as_global.append(globvar)
                        if not is_global_identified(globvar):
                            GLOBAL_SYMBOL_LIST.append(globvar)
            elif st[0] == 282:
                parse_import(st[1])
            elif st[0] == 300 and len(st) == 5:
                GLOBAL_SYMBOL_LIST.append(Variable(st[4][1])) # тут должно быть возможно не определена
                pass
            else:
                for j in range(1, len(st)):
                    if st[j][0] == 279:

                        parse_right_part(st[j])
                        r = parse_type_of_arith_expr(st[j][2], self.visible_names+self.local_names)
                        self.return_type = r
                    elif  (st[j][0] == 271 and st[j][2][1]=='='):
                        r = parse_type_of_arith_expr(st[j][3], self.visible_names+self.local_names)
                        self.return_type = r
                        parse_right_part(st[j][3])
                        add_var(st[j][1], r)
                    else:
                        self.parse(st[j], visible, type_var)
        else:
            return


class Function(Callable):
    def __init__(self, name, visible_names = [], global_names=[], local_names=[], body=[], args=[], return_type=None):
        Callable.__init__(self, name, visible_names, global_names, local_names, body, args, return_type)


class ClassMethod(Callable):
    def __init__(self, name, visible_names =[], global_names=[], local_names=[], body=[], args=[], return_type=None):
        Callable.__init__(self, name, visible_names, global_names, local_names, body, args, return_type)


class BaseModule(Name):
    """ super class for modules and classes
    """
    def __init__(self, name, body=[]):
        Name.__init__(self, name)
        self.body = body


class Class(BaseModule):
    def __init__(self, name, body=[]):
        BaseModule.__init__(self, name, body)



class Module(BaseModule):
    def __init__(self, name, body=[]):
        BaseModule.__init__(self, name, body)
        SYMBOL_LIST = []


NON_TERMINAL = range(256, 338)  # non terminal symbols of python grammar
GLOBAL_SYMBOL_LIST = []         # list for global names
ERROR_LIST = []






def parse_args(self, st, local):
    if st[0] in NON_TERMINAL:
        if st[0] == 265:
            self.local_names.append(Variable(st[1][1]))
        else:
            for j in range(1,len(st)):
                self.parse_args(st[j], local)
    else:
        return

def parse_type_of_right_part(st):
    if st[0] == 316:
        return parse_type_of_arith_expr(st)
    else:
        return parse_type_of_right_part(st[1])


from parse_csv import description
op_descr={
    '+': '__add__',
    '-': '__sub__',
    '/': '__truediv__',
    '//': '__floordiv__',
    '*': '__mul__'
}
reversed_typeIDS = dict(zip(type_IDS.values(),type_IDS.keys()))

def var_or_func(st, st271):
        if st[0] in NON_TERMINAL:
            if st[0] == 319 and len(st) == 3 and st[2][0] == 322:
                v_name = st[1][1][1]
                sym = Name(v_name)
                for s in GLOBAL_SYMBOL_LIST:
                    if isinstance(s, Function) and s.name == sym.name and len(s.body) >= 1:
                        s.parse(s.body, GLOBAL_SYMBOL_LIST)
                        for p in s.local_names:
                            if isinstance(p, Function) and len(p.body) >= 1:
                                p.parse(p.body, p.visible_names + GLOBAL_SYMBOL_LIST)
                        break
            else:
                for j in range(1,len(st)):
                    var_or_call(st[j],st271)


def parse_type_of_arith_expr(st, sym_list=GLOBAL_SYMBOL_LIST):
    result = type_IDS['UNDEFINED']
    if (st[0] == 316 or st[0]==317) and len(st) >=4:
            i = 1
            while i < len(st) - 1:
                if i == 1:
                    left = parse_type_of_arith_expr(st[i])
                    op = op_descr[st[i+1][1]]
                    right = parse_type_of_arith_expr(st[i+2])
                    # result = type_IDS['UNDEFINED']
                    try:
                        v = reversed_typeIDS[left]
                    except KeyError:
                        break
                    try:
                        if isinstance(right, int):
                            for j in description[v][op]:
                                if right in j.keys():
                                    result = j[right]
                                    break
                            else:
                                err = analizer_instance.Error(st[i+1][2], st[i+1][3], 1, "Not compatible types")
                                if err not in ERROR_LIST:
                                    ERROR_LIST.append(err)
                    except KeyError:
                        err = analizer_instance.Error(st[i+1][2], st[i+1][3], 1, "Not compatible types")
                        if err not in ERROR_LIST:
                            ERROR_LIST.append(err)
                    i += 2
                else:
                    left = result
                    op = op_descr[st[i+1][1]]
                    right = parse_type_of_arith_expr(st[i+2])
                    # result = type_IDS['UNDEFINED']
                    try:
                        v = reversed_typeIDS[left]
                    except KeyError:
                        break
                    try:
                        for j in description[v][op]:
                            if right in j.keys():
                                result = j[right]
                                break
                        else:
                            err = analizer_instance.Error(st[i+1][2], st[i+1][3], 1, "Not compatible types")
                            if err not in ERROR_LIST:
                                ERROR_LIST.append(err)
                    except KeyError:
                        err = analizer_instance.Error(st[i+1][2], st[i+1][3], 1, "Not compatible types")
                        if err not in ERROR_LIST:
                            ERROR_LIST.append(err)
                    i += 2
        # print(result)
    # elif st[0] == 271 and len(st) == 2:
    #             pass # var_or_call(st, st)
    elif st[0] == 320:
        if len(st) == 2 and st[1][0] != 1:
            if st[1][1].startswith("'"):
                result=type_IDS['str']
                # return result
            try:
                int(st[1][1])
                result = type_IDS['int']
                # return result
                # print (result)
            except:
                pass
            try:
                float(st[1][1])
                result = type_IDS['float']
                # return result
                # print (result)
            except:
                pass
        elif len(st) == 2 and st[1][0] == 1:
            #if Name(st[1][1]) in sym_list:
                for i in sym_list:
                    if isinstance(i, Variable) and i.name == st[1][1]:
                        return i.type
                    elif isinstance(i, Function) and i.name == st[1][1]:
                        i.do_all(i.body, i.local_names+GLOBAL_SYMBOL_LIST)
                        return i.return_type
    elif len(st) >= 2:
        return parse_type_of_arith_expr(st[1], sym_list)
    if result == 15:
        pass
    return result
    pass


def parse_type_of_constants(st):
    pass




def parse_main(st):
    def add_var(st, type_var=type_IDS['UNDEFINED']):
        if st[0] == 320 and not keyword.iskeyword(st[1][1]) and st[1][0] == token.NAME:
            GLOBAL_SYMBOL_LIST.append(Variable(st[1][1], type_var))
        else:
            for j in range(1,len(st)):
                if st[j][0] in NON_TERMINAL:
                    add_var(st[j], type_var)
    def parse_right_part(st):
        # result = parse_type_of_arith_expr(st)
        # print (result)
        if st[0] in NON_TERMINAL:
            if st[0] == 319 and len(st) > 2 and st[1][1] == token.NAME:
                var_name = st[1][1][1]
                if not isinstance(st[2], int):
                    for name in st[2]:
                        if not isinstance(name, int):
                            var_name += name[1]
                if not is_identified(Name(var_name)):
                    err = analizer_instance.Error(st[1][1][2]-1, st[1][1][3], len(var_name), "Undefined variable")
                    # err = MyError(st[1][1][2], st[1][1][3], "error, undefined variable" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                    if err not in ERROR_LIST:
                        ERROR_LIST.append(err)
                else:
                    for j in range(1,len(st)):
                        parse_right_part(st[j])
            elif (st[0] == 320) and (st[1][0] == token.NAME) and (not is_identified(Name(st[1][1]))):
                err = analizer_instance.Error(st[1][2]-1, st[1][3], len(st[1][1]), "Undefined variable")
                # err = MyError(st[1][2], st[1][3], "error, undefined variable" + " line " + str(st[1][2]) + " position " + str(st[1][3]))
                if err not in ERROR_LIST:
                    ERROR_LIST.append(err)
            elif (st[0] == 320) and len(st)>2 and (st[2][0]==321):
                parse_compound_stmt(st[2])
            elif st[0] == 331 and len(st) == 4:
                add_var(st[1])
                parse_right_part(st[3])
            else:
                for j in range(1, len(st)):
                    parse_right_part(st[j])

    def is_identified(sym):
        for s in GLOBAL_SYMBOL_LIST:
            if sym.name == s.name:
                return True
        return False

    def var_or_call(st, st271):
        if st[0] in NON_TERMINAL:
            if st[0] == 319 and len(st) == 3 and st[2][0] == 322:
                v_name = st[1][1][1]
                if st[2][1][1] == '.':
                    for name in st[2]:
                        if not isinstance(name, int):
                            v_name += name[1]
                else:
                    parse_right_part(st[2])
                sym = Name(v_name)
                if is_identified(sym):
                    for s in GLOBAL_SYMBOL_LIST:
                        if isinstance(s, Function) and s.name == sym.name and len(s.body) >= 1:
                            s.parse(s.body, GLOBAL_SYMBOL_LIST)
                            for p in s.local_names:
                                if isinstance(p, Function) and len(p.body) >= 1:
                                    p.parse(p.body, p.visible_names + GLOBAL_SYMBOL_LIST)
                            break
                else:
                    err = analizer_instance.Error(st[1][1][2]-1, st[1][1][3], len(sym.name), "Undefined function")
                    # err = MyError(st[1][1][2],st[1][1][3],"error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                    if err not in ERROR_LIST:
                        ERROR_LIST.append(err)
            elif st[0] == 319 and len(st)!=3:
                parse_right_part(st271)
            else:
                for j in range(1,len(st)):
                    var_or_call(st[j],st271)



    def parse_compound_stmt(st):
        if st[0] == 262:
            GLOBAL_SYMBOL_LIST.append(Function(st[2][1],GLOBAL_SYMBOL_LIST,GLOBAL_SYMBOL_LIST,[],st[5],st[3]))
            GLOBAL_SYMBOL_LIST[len(GLOBAL_SYMBOL_LIST)-1].parse_args(GLOBAL_SYMBOL_LIST[len(GLOBAL_SYMBOL_LIST)-1].args, GLOBAL_SYMBOL_LIST[len(GLOBAL_SYMBOL_LIST)-1].local_names)

        elif st[0] == 296:
            parse_right_part(st[4])
            add_var(st[2])
            parse(st[6])
        elif st[0] == 329:
            GLOBAL_SYMBOL_LIST.append(Class(st[2][1],st))
        elif st[0] == 294:
            for statement in st:
                if not isinstance(statement,int) and statement[0] == 302:
                    parse_right_part(statement)
                elif not isinstance(statement,int):
                    parse(statement)
        elif st[0] == 321 and len(st)>2 and st[2] == 333:
            add_var(st[2][2])
            parse_right_part(st[1])
            parse_right_part(st[2][4])
        elif st[0] == 321 and len(st) == 2:
            parse_right_part(st[1])
        else:
            parse(st)

    def parse_import(st):
        if st[0] == 283:
            import_name(st[2])
        elif st[0] == 284:
            module_name = ""
            if type(st[2]) != type(1):
                for name in st[2]:
                    if type(name) != type(1):
                        module_name += name[1]
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                print("Import Error, No module named " + module_name)
                exit()
            if len(st)==5 and st[4][1] == "*":
                syms = inspect.getmembers(module)
                str_syms = dir(module)
                name_as = ""
                for sym in syms:
                    if inspect.isfunction(sym[1]):
                        GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.isbuiltin(sym[1]):
                        GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.ismethod(sym[1]):
                        pass
                    elif inspect.isgeneratorfunction:
                        GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.isgenerator(sym[1]):
                        pass
                    elif inspect.istraceback(sym[1]):
                        pass
                    elif inspect.isframe(sym[1]):
                        pass
                    elif inspect.iscode(sym[1]):
                        pass
                    elif inspect.isroutine(sym[1]):
                        pass
                    elif inspect.isabstract(sym[1]):
                        pass
                    elif inspect.ismemberdescriptor(sym[1]):
                        pass
                    elif inspect.isdatadescriptor(sym[1]):
                        pass
                    elif inspect.isdatadescriptor(sym[1]):
                        pass
                    elif inspect.isgetsetdescriptor(sym[1]):
                        pass
                    elif inspect.ismemberdescriptor(sym[1]):
                        pass
                    elif inspect.isclass(sym[1]):
                        GLOBAL_SYMBOL_LIST.append(Class(sym[0]))
                    else:
                        print(sym[0])
            else:
                for counter in range(len(st[4])):
                    if not isinstance(st[4][counter],int) and st[4][counter][0] == 285:
                        import_from(st[4][counter], module)

    def import_name(s1):
        if s1[0] in NON_TERMINAL:
            if s1[0] in NON_TERMINAL and s1[0] == 286:
                dot_name = ""
                module_name = ""
                for name in s1[1]:
                    if type(name) != type(1):
                        module_name += name[1]
                if len(s1) == 2:
                    dot_name = module_name
                elif len(s1) == 4:
                    dot_name = s1[3][1]
                try:
                    module = importlib.import_module(module_name)
                except ImportError:
                    print("Import Error, No module named " + module_name)
                    exit()

                a = dir(module)
                new_module = Module(module_name)
                new_module.SYMBOL_LIST = []
                syms = inspect.getmembers(module)
                for sym in syms:
                    if inspect.isfunction(sym[1]):
                        #new_module.SYMBOL_LIST.append(Function(dot_name+'.' + sym[0]))
                        new_module.SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.isbuiltin(sym[1]):
                        new_module.SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.ismethod(sym[1]):
                        pass
                    elif inspect.isgeneratorfunction:
                        new_module.SYMBOL_LIST.append(Function(sym[0]))
                        #new_module.SYMBOL_LIST.append(Variable(sym[0]))
                    elif inspect.isgenerator(sym[1]):
                        pass
                    elif inspect.istraceback(sym[1]):
                        pass
                    elif inspect.isframe(sym[1]):
                        pass
                    elif inspect.iscode(sym[1]):
                        pass
                    elif inspect.isroutine(sym[1]):
                        pass
                    elif inspect.isabstract(sym[1]):
                        pass
                    elif inspect.ismemberdescriptor(sym[1]):
                        pass
                    elif inspect.isdatadescriptor(sym[1]):
                        pass
                    elif inspect.isdatadescriptor(sym[1]):
                        pass
                    elif inspect.isgetsetdescriptor(sym[1]):
                        pass
                    elif inspect.ismemberdescriptor(sym[1]):
                        pass
                    elif inspect.isclass(sym[1]):
                        new_module.SYMBOL_LIST.append(Class(sym[0], [], []))
                    else:
                        print(sym[0])
                GLOBAL_SYMBOL_LIST.append(new_module)
            else:
                for j in range(1,len(s1)):
                    import_name(s1[j])

    def import_from(s1, module):
        syms = inspect.getmembers(module)
        str_syms = dir(module)
        name_as = ""
        if len(s1) == 4:
            name_as = s1[3][1]


        if not (s1[1][1] in str_syms):
            print("import error")
            exit()
        else:
            for sym in syms:
                if sym[0] == s1[1][1]:
                    if inspect.isfunction(sym[1]):
                        if len(s1) == 4:
                            GLOBAL_SYMBOL_LIST.append(Function(name_as))
                        else:
                            GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.isbuiltin(sym[1]):
                        if len(s1) == 4:
                            GLOBAL_SYMBOL_LIST.append(Function(name_as))
                        else:
                            GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.ismethod(sym[1]):
                        pass
                    elif inspect.isgeneratorfunction:
                        if len(s1) == 4:
                            GLOBAL_SYMBOL_LIST.append(Function(name_as))
                        else:
                            GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.isgenerator(sym[1]):
                        pass
                    elif inspect.istraceback(sym[1]):
                        pass
                    elif inspect.isframe(sym[1]):
                        pass
                    elif inspect.iscode(sym[1]):
                        pass
                    elif inspect.isroutine(sym[1]):
                        pass
                    elif inspect.isabstract(sym[1]):
                        pass
                    elif inspect.ismemberdescriptor(sym[1]):
                        pass
                    elif inspect.isdatadescriptor(sym[1]):
                        pass
                    elif inspect.isdatadescriptor(sym[1]):
                        pass
                    elif inspect.isgetsetdescriptor(sym[1]):
                        pass
                    elif inspect.ismemberdescriptor(sym[1]):
                        pass
                    elif inspect.isclass(sym[1]):
                        if len(s1) == 4:
                            GLOBAL_SYMBOL_LIST.append(Class(name_as))
                        else:
                            GLOBAL_SYMBOL_LIST.append(Class(sym[0]))
                    else:
                        print(sym[0])

    def import_builtin():
        module = importlib.import_module('builtins')
        syms = inspect.getmembers(module)
        for sym in syms:
            if inspect.isfunction(sym[1]):
                GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
            elif inspect.isbuiltin(sym[1]):
                GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
            elif inspect.ismethod(sym[1]):
                pass
            elif inspect.isgeneratorfunction:
                GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
            elif inspect.isgenerator(sym[1]):
                pass
            elif inspect.istraceback(sym[1]):
                pass
            elif inspect.isframe(sym[1]):
                pass
            elif inspect.iscode(sym[1]):
                pass
            elif inspect.isroutine(sym[1]):
                pass
            elif inspect.isabstract(sym[1]):
                pass
            elif inspect.ismemberdescriptor(sym[1]):
                pass
            elif inspect.isdatadescriptor(sym[1]):
                pass
            elif inspect.isdatadescriptor(sym[1]):
                pass
            elif inspect.isgetsetdescriptor(sym[1]):
                pass
            elif inspect.ismemberdescriptor(sym[1]):
                pass
            elif inspect.isclass(sym[1]):
                GLOBAL_SYMBOL_LIST.append(Class(sym[0]))
            else:
                print(sym[0])

    import_builtin()


    def parse(st, type_var=type_IDS['UNDEFINED']):
        if len(st) > 0 and st[0] in NON_TERMINAL:
            if st[0] == 271 and len(st) == 4 and st[2][0] != 273:
                parse_right_part(st[3])
                r = parse_type_of_arith_expr(st[3])
                parse(st[1], r)
            elif st[0] == 323:
                parse_right_part(st)
            elif st[0] == 271 and len(st) == 4 and st[2][0] == 273:
                parse_right_part(st[1])
                parse_right_part(st[3])
            elif st[0] == 271 and len(st) == 2:
                var_or_call(st, st)
            elif st[0] == 320 and not keyword.iskeyword(st[1][1]) and st[1][0] == token.NAME and not is_identified(Variable(st[1][1], type_var)):
                GLOBAL_SYMBOL_LIST.append(Variable(st[1][1], type_var))
            elif st[0] == 293:
                parse_compound_stmt(st[1])
            elif st[0] == 290:
                for j in range(2, len(st)):
                    if st[j][0] == 1:
                        globvar = Variable(st[j][1], type_var)
                        globvar.initialized = False
                        if (globvar not in GLOBAL_SYMBOL_LIST) and (Variable(st[j][1], type_var) not in GLOBAL_SYMBOL_LIST):
                            GLOBAL_SYMBOL_LIST.append(globvar)
            elif st[0] == 282:
                parse_import(st[1])
            elif st[0] == 300 and len(st) == 5:
                GLOBAL_SYMBOL_LIST.append(Variable(st[4][1], type_var)) # тут должно быть возможно не определена
            else:
                for j in range(1, len(st)):

                    if st[j][0] == 279:

                        parse_right_part(st[j])
                        #r = parse_type_of_arith_expr(st[j][2], GLOBAL_SYMBOL_LIST)
                        #self.return_type = r
                    elif  (st[j][0] == 271 and st[j][2][1]=='='):
                        r = parse_type_of_arith_expr(st[j][3], GLOBAL_SYMBOL_LIST)
                        #self.return_type = r
                        parse_right_part(st[j][3])
                        add_var(st[j][1], r)
                    else:
                        parse(st[j], type_var)
        else:
            return

    parse(st)


class MyError:
    def __init__(self, row, col, info, ID = 0):
        self.row = row
        self.col = col
        self.id = ID
        self.info = info

    def __eq__(self, other):
        if self.row == other.row and self.col == other.col and self.id == other.id:
            return True
        else:
            return False


def run_static_analisys(source_code_str):
    try:
        a = compile(source_code_str, '', 'exec')
    except Exception as error:
        if isinstance("", SyntaxError):
            message = {'type': 'F',
                       'row': error.lineno,
                       'column': error.offset,
                       'text': error.message}
        else:
            message = {'type': 'F',
                       'row': -1,
                       'column': -1,
                       'text': str(error)}
        print(message)
        #exit()
        return

    GLOBAL_SYMBOL_LIST.append(Variable("__file__"))
    st_main = parser.suite(source_code_str)
    statements = parser.st2list(st_main, line_info=True, col_info=True)

    parse_main(statements)


    for s in GLOBAL_SYMBOL_LIST:
        if isinstance(s, Function) and len(s.body) >= 1:
            s.do_all(s.body, GLOBAL_SYMBOL_LIST)


def get_errors():
    global ERROR_LIST
    return ERROR_LIST


def clear_errors():
    global ERROR_LIST
    ERROR_LIST.clear()

if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__)) + "/"
    test_name = "MyTests/test7.py"
    source_file = open(base + test_name, 'r')
    source_code_str = source_file.read()
    source_file.close()


    try:
        a = compile(source_code_str, '', 'exec')
    except Exception as error:
        if isinstance("", SyntaxError):
            message = {'type': 'F',
                       'row': error.lineno,
                       'column': error.offset,
                       'text': error.message}
        else:
            message = {'type': 'F',
                       'row': -1,
                       'column': -1,
                       'text': str(error)}
        print(message)
        exit()


    GLOBAL_SYMBOL_LIST.append(Variable("__file__"))
    st_main = parser.suite(source_code_str)
    statements = parser.st2list(st_main, line_info=True, col_info=True)

    parse_main(statements)


    for s in GLOBAL_SYMBOL_LIST:
        if isinstance(s, Function) and len(s.body) >= 1:
            s.do_all(s.body, GLOBAL_SYMBOL_LIST)


    for err in ERROR_LIST:
        print(err.message + ", line "+str( err.line_no)+", column " + str( err.start_pos))