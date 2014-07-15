from tokenize import generate_tokens, tokenize
import keyword
import token
from io import BytesIO
import parser
import importlib
import inspect


class Name:
    def __init__(self, name, visible_names = []):
        self.name = name
        self.visible_names = visible_names


class Variable(Name):
    def __init__(self, name):
        Name.__init__(self, name)


class Callable(Name):
    def __init__(self, name, visible_names = [], global_names=[], local_names=[], body=[], args=[], return_type=None):
        Name.__init__(self, name)
        self.body = []; self.body += body
        self.args = []; self.args += args
        self.return_type = []; self.return_type+=[(return_type)]
        self.local_names = []; self.local_names+=(local_names)
        self.global_names = []; self.global_names+=(global_names)
        self.visible_names = []; self.visible_names+=(visible_names)
    def parse(self, st, visible):
        def parse_right_part(st):
            if st[0] in NON_TERMINAL:
                #module_name = ""
                #if type(st[2]) != type(1):
                #    for name in st[2]:
                #                if type(name) != type(1):
                #                    module_name += name[1]
                if (st[0] == 319) and len(st) > 2 and st[1][1] == token.NAME:
                    var_name = st[1][1][1]
                    if type(st[2]) != type(1):
                        for name in st[2]:
                            if type(name) != type(1):
                                var_name += name[1]
                    if not is_local_identified(Name(var_name)) and not is_global_identified(Name(var_name)):
                        err = Error(st[1][1][2], st[1][1][3], "error, undefined variable" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                        if err not in ERROR_LIST:
                            ERROR_LIST.append(err)
                elif (st[0] == 320) and (st[1][0] == token.NAME) and (not is_local_identified(Name(st[1][1]))) and (not is_global_identified(Name(st[1][1]))):
                    err = Error(st[1][2], st[1][3], "error, undefined variable" + " line " + str(st[1][2]) + " position " + str(st[1][3]))
                    if err not in ERROR_LIST:
                        ERROR_LIST.append(err)
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

        def var_or_call(st,st271):
            if st[0] in NON_TERMINAL:
                if st[0] == 319 and len(st)==3 and st[2][0] == 322:
                    v_name = st[1][1][1]
                    if st[2][1][1] == '.':
                        for name in st[2]:
                            if type(name) != type(1):
                                v_name += name[1]
                    sym = Name(v_name)
                    if is_local_identified(sym):
                        for s in self.local_names:
                            if type(s) == type(Function("",[],[])) and s.name == sym.name and len(s.body)>=1:
                                s.parse(s.body, self.visible_names + self.local_names)
                                for p in s.local_names:
                                    if type(p) == type(Function("",[],[])) and len(p.body)>1:
                                        p.parse(p.body,p.visible_names + self.local_names)
                                break
                    elif is_global_identified(sym):
                        for s in self.local_names:
                            if type(s) == type(Function("",[],[])) and s.name == sym.name and len(s.body)>=1:
                                s.parse(s.body, self.visible_names + self.local_names)
                                for p in s.local_names:
                                    if type(p) == type(Function("",[],[])) and len(p.body)>1:
                                        p.parse(p.body,p.visible_names + self.local_names)
                                break
                    else:
                        err = Error(st[1][1][2],st[1][1][3],"error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                        if err not in ERROR_LIST:
                            ERROR_LIST.append(err)
                        #print("error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                elif st[0] == 319 and len(st)!=3:
                    parse_right_part(st271)
                else:
                    for j in range(1,len(st)):
                        var_or_call(st[j],st271)


        def add_var(st):
            if st[0] == 320 and not keyword.iskeyword(st[1][1]):
                self.local_names.append(Variable(st[1][1]))
            else:
                for j in range(1,len(st)):
                    if st[j][0] in NON_TERMINAL:
                        add_var(st[j])

        def parse_compound_stmt(st, visible):
            if st[0] == 262:
                self.local_names.append(Function(st[2][1],visible + self.local_names,GLOBAL_SYMBOL_LIST,[],st[5],st[3]))
            elif st[0] == 296:
                parse_right_part(st[4])
                add_var(st[2])
                self.parse(st[6],self.visible_names)
            elif st[0] == 329:
                GLOBAL_SYMBOL_LIST.append(Class(st[2][1],st))
            else:
                parse_right_part(st)

        def parse_import(st):
            if(st[0] == 283):
                import_name(st[2])
            elif st[0] == 284:
                #pass
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
                import_from(st[4], module)

            pass
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
                        syms = inspect.getmembers(module)
                        for sym in syms:
                            if inspect.isfunction(sym[1]):
                                self.local_names.append(Function(dot_name+'.' + sym[0]))
                            elif inspect.isbuiltin(sym[1]):
                                self.local_names.append(Function(dot_name+'.' + sym[0]))
                            elif inspect.ismethod(sym[1]):
                                pass
                            elif inspect.isgeneratorfunction:
                                self.local_names.append(Function(dot_name+'.' + sym[0]))
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
                                self.local_names.append(Class(dot_name+'.' + sym[0], [], []))
                            else:
                                print(sym[0])
                    else:
                        for j in range(1,len(s1)):
                            import_name(s1[j])

        def import_from(s1, module):
            syms = inspect.getmembers(module)
            str_syms = dir(module)
            name_as = ""
            if len(s1[1]) == 4:
                name_as = s1[1][3][1]

            if (s1[1] == '*'):
                for sym in syms:
                    if inspect.isfunction(sym[1]):
                        if len(s1[1]) == 4:
                            self.local_names.append(Function(name_as))
                        else:
                            self.local_names.append(Function(sym[0]))
                    elif inspect.isbuiltin(sym[1]):
                        if len(s1[1]) == 4:
                            self.local_names.append(Function(name_as))
                        else:
                            self.local_names.append(Function(sym[0]))
                    elif inspect.ismethod(sym[1]):
                        pass
                    elif inspect.isgeneratorfunction:
                        if len(s1[1]) == 4:
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
                        if len(s1[1]) == 4:
                            self.local_names.append(Class(name_as))
                        else:
                            self.local_names.append(Class(sym[0]))
                    else:
                        print(sym[0])
            elif not (s1[1][1][1] in str_syms):
                print("import error")
                exit()
            else:
                for sym in syms:
                    if sym[0] == s1[1][1][1]:
                        if inspect.isfunction(sym[1]):
                            if len(s1[1]) == 4:
                                self.local_names.append(Function(name_as))
                            else:
                                self.local_names.append(Function(sym[0]))
                        elif inspect.isbuiltin(sym[1]):
                            if len(s1[1]) == 4:
                                self.local_names.append(Function(name_as))
                            else:
                                self.local_names.append(Function(sym[0]))
                        elif inspect.ismethod(sym[1]):
                            pass
                        elif inspect.isgeneratorfunction:
                            if len(s1[1]) == 4:
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
                            if len(s1[1]) == 4:
                                self.local_names.append(Class(name_as))
                            else:
                                self.local_names.append(Class(sym[0]))
                        else:
                            print(sym[0])

        if len(st) > 0 and st[0] in NON_TERMINAL:
            if st[0] == 271 and len(st) == 4 and st[2][0] != 273:
                self.parse(st[1],visible)
                parse_right_part(st[3])
            elif st[0] == 271 and len(st) == 4 and st[2][0] == 273:
                parse_right_part(st[1])
                parse_right_part(st[3])
            elif st[0] == 271 and len(st) == 2:
                pass
                var_or_call(st,st)
            elif st[0] == 320 and not keyword.iskeyword(st[1][1]):
                self.local_names.append(Variable(st[1][1]))
            elif st[0] == 293:
                pass
                parse_compound_stmt(st[1], visible)
            elif st[0] == 290:
                for j in range(2, len(st)):
                    if st[j][0] == 1:
                        GLOBAL_SYMBOL_LIST.append(Variable(st[j][1]))
            elif st[0] == 282:
                pass
                parse_import(st[1])
            else:
                for j in range(1, len(st)):
                    if st[j][0] == 279:
                        pass
                        parse_right_part(st[j])
                    else:
                        self.parse(st[j],visible)
        else:
            return

        pass

class Function(Callable):
    def __init__(self, name, visible_names = [], global_names=[], local_names=[], body=[], args=[], return_type=None):
        Callable.__init__(self, name, visible_names, global_names, local_names, body, args, return_type)


class ClassMethod(Callable):
    def __init__(self, name, visible_names =[], global_names=[], local_names=[], body=[], args=[], return_type=None):
        Callable.__init__(self, name, visible_names, global_names, local_names, body, args, return_type)


class BaseModule(Name):
    def __init__(self, name, body=[]):
        Name.__init__(self, name)
        self.body = body


class Class(BaseModule):
    def __init__(self, name, body=[]):
        BaseModule.__init__(self, name, body)



class Module(BaseModule):
    def __init__(self, name, body=[]):
        BaseModule.__init__(self, name, body)


NON_TERMINAL = range(256, 338)
GLOBAL_SYMBOL_LIST = []
ERROR_LIST = []


def parse_main(st):
    def parse_right_part(st):
        if st[0] in NON_TERMINAL:
            if (st[0] == 319 and len(st) > 2 and st[1][1] == token.NAME):
                    var_name = st[1][1][1]
                    if type(st[2]) != type(1):
                        for name in st[2]:
                            if type(name) != type(1):
                                var_name += name[1]
                    if not is_identified(Name(var_name)):
                        err = Error(st[1][1][2], st[1][1][3], "error, undefined variable" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                        if err not in ERROR_LIST:
                            ERROR_LIST.append(err)
                    else:
                        for j in range(1,len(st)):
                            parse_right_part(st[j])
            elif (st[0] == 320) and (st[1][0] == token.NAME) and (not is_identified(Name(st[1][1]))):
                err = Error(st[1][2], st[1][3], "error, undefined variable" + " line " + str(st[1][2]) + " position " + str(st[1][3]))
                if err not in ERROR_LIST:
                    ERROR_LIST.append(err)
            else:
                for j in range(1,len(st)):
                    parse_right_part(st[j])

    def is_identified(sym):
        for s in GLOBAL_SYMBOL_LIST:
            if sym.name == s.name:
                return True
        return False
    def var_or_call(st,st271):
        if st[0] in NON_TERMINAL:
            if st[0] == 319 and len(st)==3 and st[2][0] == 322:
                v_name = st[1][1][1]
                if st[2][1][1] == '.':
                    for name in st[2]:
                        if type(name) != type(1):
                            v_name += name[1]
                sym = Name(v_name)
                if is_identified(sym):
                    for s in GLOBAL_SYMBOL_LIST:
                        if type(s) == type(Function("",[],[])) and s.name == sym.name and len(s.body)>=1:
                            s.parse(s.body, GLOBAL_SYMBOL_LIST)
                            for p in s.local_names:
                                    if type(p) == type(Function("",[],[])) and len(p.body)>1:
                                        p.parse(p.body,p.visible_names + GLOBAL_SYMBOL_LIST)
                            break
                else:
                    err = Error(st[1][1][2],st[1][1][3],"error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                    if err not in ERROR_LIST:
                        ERROR_LIST.append(err)
                    #print("error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
            elif st[0] == 319 and len(st)!=3:
                parse_right_part(st271)
            else:
                for j in range(1,len(st)):
                    var_or_call(st[j],st271)


    def add_var(st):
        if st[0] == 320 and not keyword.iskeyword(st[1][1]):
            GLOBAL_SYMBOL_LIST.append(Variable(st[1][1]))
        else:
            for j in range(1,len(st)):
                if st[j][0] in NON_TERMINAL:
                    add_var(st[j])

    def parse_compound_stmt(st):
        if st[0] == 262:
            GLOBAL_SYMBOL_LIST.append(Function(st[2][1],GLOBAL_SYMBOL_LIST,GLOBAL_SYMBOL_LIST,[],st[5],st[3]))
        elif st[0] == 296:
            parse_right_part(st[4])
            add_var(st[2])
            parse(st[6])
        elif st[0] == 329:
            GLOBAL_SYMBOL_LIST.append(Class(st[2][1],st))
        elif st[0] == 294:
            parse(st[1])
        else:
            parse_right_part(st)

    def parse_import(st):
        if(st[0] == 283):
            import_name(st[2])
        elif st[0] == 284:
            #pass
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
            import_from(st[4], module)

        pass
    import inspect
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
                    syms = inspect.getmembers(module)
                    for sym in syms:
                        if inspect.isfunction(sym[1]):
                            GLOBAL_SYMBOL_LIST.append(Function(dot_name+'.' + sym[0]))
                        elif inspect.isbuiltin(sym[1]):
                            GLOBAL_SYMBOL_LIST.append(Function(dot_name+'.' + sym[0]))
                        elif inspect.ismethod(sym[1]):
                            pass
                        elif inspect.isgeneratorfunction:
                            GLOBAL_SYMBOL_LIST.append(Function(dot_name+'.' + sym[0]))
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
                            GLOBAL_SYMBOL_LIST.append(Class(dot_name+'.' + sym[0], [], []))
                        else:
                            print(sym[0])
                else:
                    for j in range(1,len(s1)):
                        import_name(s1[j])

    def import_from(s1, module):
        syms = inspect.getmembers(module)
        str_syms = dir(module)
        name_as = ""
        if len(s1[1]) == 4:
            name_as = s1[1][3][1]

        if (s1[1] == '*'):
            for sym in syms:
                if inspect.isfunction(sym[1]):
                    if len(s1[1]) == 4:
                        GLOBAL_SYMBOL_LIST.append(Function(name_as))
                    else:
                        GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                elif inspect.isbuiltin(sym[1]):
                    if len(s1[1]) == 4:
                        GLOBAL_SYMBOL_LIST.append(Function(name_as))
                    else:
                        GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                elif inspect.ismethod(sym[1]):
                    pass
                elif inspect.isgeneratorfunction:
                    if len(s1[1]) == 4:
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
                    if len(s1[1]) == 4:
                        GLOBAL_SYMBOL_LIST.append(Class(name_as))
                    else:
                        GLOBAL_SYMBOL_LIST.append(Class(sym[0]))
                else:
                    print(sym[0])
        elif not (s1[1][1][1] in str_syms):
            print("import error")
            exit()
        else:
            for sym in syms:
                if sym[0] == s1[1][1][1]:
                    if inspect.isfunction(sym[1]):
                        if len(s1[1]) == 4:
                            GLOBAL_SYMBOL_LIST.append(Function(name_as))
                        else:
                            GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.isbuiltin(sym[1]):
                        if len(s1[1]) == 4:
                            GLOBAL_SYMBOL_LIST.append(Function(name_as))
                        else:
                            GLOBAL_SYMBOL_LIST.append(Function(sym[0]))
                    elif inspect.ismethod(sym[1]):
                        pass
                    elif inspect.isgeneratorfunction:
                        if len(s1[1]) == 4:
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
                        if len(s1[1]) == 4:
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
                #print(sym[0])
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


    def parse(st):
        if len(st) > 0 and st[0] in NON_TERMINAL:
            if st[0] == 271 and len(st) == 4 and st[2][0] != 273:
                parse_right_part(st[3])
                parse(st[1])
            elif st[0] == 271 and len(st) == 4 and st[2][0] == 273:
                parse_right_part(st[1])
                parse_right_part(st[3])
            elif st[0] == 271 and len(st) == 2:
                pass
                var_or_call(st,st)
            elif st[0] == 320 and not keyword.iskeyword(st[1][1]):
                GLOBAL_SYMBOL_LIST.append(Variable(st[1][1]))
            elif st[0] == 293:
                pass
                parse_compound_stmt(st[1])
            elif st[0] == 290:
                for j in range(2, len(st)):
                    if st[j][0] == 1:
                        GLOBAL_SYMBOL_LIST.append(Variable(st[j][1]))
            elif st[0] == 282:
                pass
                parse_import(st[1])
            else:
                for j in range(1, len(st)):
                    if st[j][0] == 279:
                        pass
                        parse_right_part(st[j])
                    else:
                        pass
                        parse(st[j])
        else:
            return

    parse(st)


class Error:
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








if __name__ == "__main__":
    import sys
    for j in range(1,len(sys.argv)):
        file_str = (str(sys.argv[j]))
        file = open(file_str, 'r')
        source_code_str = file.read()
        file.close()
        print(file_str + ":")
        try:
            a = compile(source_code_str, '', 'exec')
        except Exception as error:
            if isinstance("",SyntaxError):
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


        st_main = parser.suite(source_code_str)
        statements = parser.st2list(st_main, line_info=True, col_info=True)

        parse_main(statements)
        for s in GLOBAL_SYMBOL_LIST:
            if type(s) == type(Function("")) and len(s.body)>=1:
                s.parse(s.body,GLOBAL_SYMBOL_LIST)




        for err in ERROR_LIST:
            print(err.info)

        GLOBAL_SYMBOL_LIST.clear()
        ERROR_LIST.clear()