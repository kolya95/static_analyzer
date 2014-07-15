from tokenize import generate_tokens, tokenize
import keyword
import token
from io import BytesIO
import parser
import importlib



nonTerminal = range(256,338)

GLOBAL_SYMBOL_LIST = []
ERROR_LIST = []

class Error:
    def __init__(self, row, col, info, ID = 0):
        self.row = row
        self.col = col
        self.id = ID
        self.info = info
    def __eq__(self, other):
        if(self.row == other.row and self.col == other.col and self.id == other.id):
            return True
        else:
            return False







class Symbol:
    def __init__(self,name):
        self.name = name

class Variable(Symbol):
    def __init__(self,name):
        self.name = name

class Function(Symbol):
    def __init__(self,name, bLine, eLine, localSym, args = [], body = []):
        self.name = name
        self.bLine = bLine
        self.eLine = eLine
        self.localSym = localSym
        self.args = args
        self.body = body
        self.globalSym = []
    def __init__(self, name, body, args):
        self.name = name
        self.body = body
        self.bLine = -1
        self.eLine = -1
        self.localSym = []
        self.args = args
        self.globalSym = []
    def body_parse(self,body_part,LOCAL_SYMBOL_LIST):
        global GLOBAL_SYMBOL_LIST
        self.func_findLocalSym(body_part,LOCAL_SYMBOL_LIST)
        for s in LOCAL_SYMBOL_LIST:
            if type(s) == type(Function("",[],[])) and len(s.body)>0:
                s.func_findLocalSym(s.body,s.localSym)
                s.body_parse(s.body,s.localSym)
    def warn_rightPart(st, LOCAL_SYMBOL_LIST):
        global ERROR_LIST
        if st[0] in nonTerminal:
            if (st[0] == 320) and (st[1][0] == token.NAME) and ( not isIdentified(Symbol(st[1][1]),LOCAL_SYMBOL_LIST) ) \
                    and (not isIdentified(Symbol(st[1][1]),GLOBAL_SYMBOL_LIST)):
                err = Error(st[1][2],st[1][3],"warning, maybe undefined variable" + " line " + str(st[1][2]) + " position " + str(st[1][3]))
                if err not in ERROR_LIST:
                    ERROR_LIST += [err]
                #print("warning, maybe undefined variable" + " line " + str(st[1][2]) + " position " + str(st[1][3]))
            else:
                for j in range(1,len(st)):
                    Function.warn_rightPart(st[j], LOCAL_SYMBOL_LIST)
    def func_findLocalSym(self,st, LOCAL_SYMBOL_LIST):
        global GLOBAL_SYMBOL_LIST
        if len(st)>=1 and st[0] in nonTerminal:
            if st[0] == 271 and len(st) == 4:
                self.func_findLocalSym(st[1], LOCAL_SYMBOL_LIST)
                Function.warn_rightPart(st[3],LOCAL_SYMBOL_LIST)
            elif st[0] == 271 and len(st) == 2:
                Function.func_VarOrFuncCall(st,LOCAL_SYMBOL_LIST,st)
            elif st[0] == 320 and not keyword.iskeyword(st[1][1]):
                LOCAL_SYMBOL_LIST += [Variable(st[1][1])]
            elif st[0] == 293:
                Function.func_compound_stmtParse(st[1],LOCAL_SYMBOL_LIST)
            elif st[0] == 290:
                for j in range(2,len(st)):
                    if(st[j][0]==1):
                        GLOBAL_SYMBOL_LIST += [Variable(st[j][1])]
            elif st[0] == 282:
                parseImport(st[1],LOCAL_SYMBOL_LIST)
            else:
                for j in range(1,len(st)):
                    if st[j][0] == 279:
                        Function.warn_rightPart(st[j], LOCAL_SYMBOL_LIST)
                    else:
                        Function.func_findLocalSym(self,st[j], LOCAL_SYMBOL_LIST)
        else:
            return
    def func_VarOrFuncCall(st,LOCAL_SYMBOL_LIST,st271):
        global  ERROR_LIST
        if st[0] in nonTerminal:
            if st[0] == 319 and len(st)==3 and st[2][0] == 322:
                v_name = st[1][1][1]
                if st[2][1][1] == '.':
                    for name in st[2]:
                        if type(name) != type(1):
                            v_name += name[1]
                sym = Symbol(v_name)
                if isIdentified(sym,LOCAL_SYMBOL_LIST):
                    for s in LOCAL_SYMBOL_LIST:
                        if type(s) == type(Function("",[],[])) and s.name == sym.name:
                            s.func_findLocalSym(s.body,s.localSym)
                            break
                else:
                    err = Error(st[1][1][2],st[1][1][3],"error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                    if err not in ERROR_LIST:
                        ERROR_LIST += [err]
                    #print("error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
            elif st[0] == 319 and len(st)!=3:
                Function.warn_rightPart(st271,LOCAL_SYMBOL_LIST)
            else:
                for j in range(1,len(st)):
                    Function.func_VarOrFuncCall(st[j], LOCAL_SYMBOL_LIST,st271)
    def func_compound_stmtParse(st,LOCAL_SYMBOL_LIST):
        if st[0] == 262:
            LOCAL_SYMBOL_LIST += [Function(st[2][1],st[5],st[3])]
        elif st[0] == 296:
            addVarInLocalSym(st[2], LOCAL_SYMBOL_LIST)
            Function.warn_rightPart(st[4], LOCAL_SYMBOL_LIST)
            Function.func_findLocalSym(st[6], LOCAL_SYMBOL_LIST)
        elif st[0] == 329:
            LOCAL_SYMBOL_LIST += [Class(st[2][1],st)]
        else:
            Function.warn_rightPart(st, LOCAL_SYMBOL_LIST)

class Class(Symbol):
    def __init__(self,name,body):
        self.name = name
        self.body = body




def VarOrFuncCall(st,LOCAL_SYMBOL_LIST,st271):
    global  ERROR_LIST
    if st[0] in nonTerminal:
        if st[0] == 319 and len(st)==3 and st[2][0] == 322:
            v_name = st[1][1][1]
            if st[2][1][1] == '.':
                for name in st[2]:
                    if type(name) != type(1):
                        v_name += name[1]
            sym = Symbol(v_name)
            if isIdentified(sym,LOCAL_SYMBOL_LIST):
                for s in LOCAL_SYMBOL_LIST:
                    if type(s) == type(Function("",[],[])) and s.name == sym.name:
                        findLocalSym(s.body,s.localSym)
                        break
            else:
                err = Error(st[1][1][2],st[1][1][3],"error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
                if err not in ERROR_LIST:
                    ERROR_LIST += [err]
                #print("error, undefined function" + " line " + str(st[1][1][2]) + " position " + str(st[1][1][3]))
        elif st[0] == 319 and len(st)!=3:
            rightPart(st271,LOCAL_SYMBOL_LIST)
        else:
            for j in range(1,len(st)):
                VarOrFuncCall(st[j], LOCAL_SYMBOL_LIST,st271)


def parseImport(st,LOCAL_SYMBOL_LIST):
    if(st[0] == 283):
        import_name(st[2],LOCAL_SYMBOL_LIST)
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
        import_from(st[4], LOCAL_SYMBOL_LIST, module)

    pass
import inspect
def import_name(s1,LOCAL_SYMBOL_LIST):
    if s1[0] in nonTerminal:
            if s1[0] in nonTerminal and s1[0] == 286:
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
                        LOCAL_SYMBOL_LIST += [Function(dot_name+ '.' + sym[0],[],[])]
                    elif inspect.isbuiltin(sym[1]):
                        LOCAL_SYMBOL_LIST += [Function(dot_name+ '.' + sym[0],[],[])]
                    elif inspect.ismethod(sym[1]):
                        pass
                    elif inspect.isgeneratorfunction:
                        LOCAL_SYMBOL_LIST += [Function(dot_name+ '.' + sym[0],[],[])]
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
                        LOCAL_SYMBOL_LIST += [Class(dot_name+ '.' +sym[0],[])]
                    else:
                        print(sym[0])
            else:
                for j in range(1,len(s1)):
                    import_name(s1[j], LOCAL_SYMBOL_LIST)

def import_from(s1,LOCAL_SYMBOL_LIST, module):
    syms = inspect.getmembers(module)
    str_syms = dir(module)
    name_as = ""
    if len(s1[1]) == 4:
        name_as = s1[1][3][1]

    if (s1[1] == '*'):
        for sym in syms:
            if inspect.isfunction(sym[1]):
                if len(s1[1]) == 4:
                    LOCAL_SYMBOL_LIST += [Function(name_as,[],[])]
                else:
                    LOCAL_SYMBOL_LIST += [Function( sym[0],[],[])]
            elif inspect.isbuiltin(sym[1]):
                if len(s1[1]) == 4:
                    LOCAL_SYMBOL_LIST += [Function(name_as,[],[])]
                else:
                    LOCAL_SYMBOL_LIST += [Function( sym[0],[],[])]
            elif inspect.ismethod(sym[1]):
                pass
            elif inspect.isgeneratorfunction:
                if len(s1[1]) == 4:
                    LOCAL_SYMBOL_LIST += [Function(name_as,[],[])]
                else:
                    LOCAL_SYMBOL_LIST += [Function( sym[0],[],[])]
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
                    LOCAL_SYMBOL_LIST += [Class(name_as,[])]
                else:
                    LOCAL_SYMBOL_LIST += [Class( sym[0],[])]
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
                        LOCAL_SYMBOL_LIST += [Function(name_as,[],[])]
                    else:
                        LOCAL_SYMBOL_LIST += [Function( sym[0],[],[])]
                elif inspect.isbuiltin(sym[1]):
                    if len(s1[1]) == 4:
                        LOCAL_SYMBOL_LIST += [Function(name_as,[],[])]
                    else:
                        LOCAL_SYMBOL_LIST += [Function( sym[0],[],[])]
                elif inspect.ismethod(sym[1]):
                    pass
                elif inspect.isgeneratorfunction:
                    if len(s1[1]) == 4:
                        LOCAL_SYMBOL_LIST += [Function(name_as,[],[])]
                    else:
                        LOCAL_SYMBOL_LIST += [Function( sym[0],[],[])]
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
                        LOCAL_SYMBOL_LIST += [Class(name_as,[])]
                    else:
                        LOCAL_SYMBOL_LIST += [Class( sym[0],[])]
                else:
                    print(sym[0])






def findLocalSym(st, LOCAL_SYMBOL_LIST):
    global GLOBAL_SYMBOL_LIST
    if len(st)>0 and st[0] in nonTerminal:
        if st[0] == 271 and len(st) == 4:
            findLocalSym(st[1], LOCAL_SYMBOL_LIST)
            rightPart(st[3],LOCAL_SYMBOL_LIST)
        elif st[0] == 271 and len(st) == 2:
            VarOrFuncCall(st,LOCAL_SYMBOL_LIST,st)
        elif st[0] == 320 and not keyword.iskeyword(st[1][1]):
            LOCAL_SYMBOL_LIST += [Variable(st[1][1])]
        elif st[0] == 293:
            compound_stmtParse(st[1],LOCAL_SYMBOL_LIST)
        elif st[0] == 290:
            for j in range(2,len(st)):
                if(st[j][0]==1):
                    GLOBAL_SYMBOL_LIST += [Variable(st[j][1])]
        elif st[0] == 282:
            parseImport(st[1],LOCAL_SYMBOL_LIST)
        else:
            for j in range(1,len(st)):
                if st[j][0] == 279:
                    rightPart(st[j])
                else:
                    findLocalSym(st[j], LOCAL_SYMBOL_LIST)
    else:
        return

def compound_stmtParse(st,LOCAL_SYMBOL_LIST):
    if st[0] == 262:
        LOCAL_SYMBOL_LIST += [Function(st[2][1],st[5],st[3])]
    elif st[0] == 296:
        addVarInLocalSym(st[2], LOCAL_SYMBOL_LIST)
        rightPart(st[4], LOCAL_SYMBOL_LIST)
        findLocalSym(st[6], LOCAL_SYMBOL_LIST)
    elif st[0] == 329:
        LOCAL_SYMBOL_LIST += [Class(st[2][1],st)]
    else:
        rightPart(st, LOCAL_SYMBOL_LIST)

def addVarInLocalSym(st, LOCAL_SYMBOL_LIST):
    if st[0] == 320 and not keyword.iskeyword(st[1][1]):
        LOCAL_SYMBOL_LIST += [Variable(st[1][1])]
    else:
        for j in range(1,len(st)):
            if st[j][0] in nonTerminal:
                addVarInLocalSym(st[j], LOCAL_SYMBOL_LIST)

def isIdentified(sym, LOCAL_SYMBOL_LIST):
    for s in LOCAL_SYMBOL_LIST:
        if sym.name == s.name:
            return True
    return False


def rightPart(st, LOCAL_SYMBOL_LIST):
    global GLOBAL_SYMBOL_LIST, ERROR_LIST
    if st[0] in nonTerminal:
        if (st[0] == 320) and (st[1][0] == token.NAME) and ( not isIdentified(Symbol(st[1][1]),LOCAL_SYMBOL_LIST) ) \
                and (not isIdentified(Symbol(st[1][1]),GLOBAL_SYMBOL_LIST)):
            err = Error(st[1][2],st[1][3],"error, undefined variable" + " line " + str(st[1][2]) + " position " + str(st[1][3]))
            if err not in ERROR_LIST:
                ERROR_LIST += [err]
            #print("error, undefined variable" + " line " + str(st[1][2]) + " position " + str(st[1][3]))
        else:
            for j in range(1,len(st)):
                rightPart(st[j], LOCAL_SYMBOL_LIST)


def addVarInGlobalSym(st):
    global GLOBAL_SYMBOL_LIST
    if st[0] == 320 and not keyword.iskeyword(st[1][1]):
        GLOBAL_SYMBOL_LIST += [Variable(st[1][1])]
    else:
        for j in range(1,len(st)):
            if st[j][0] in nonTerminal:
                addVarInGlobalSym(st[j])

if __name__ == "__main__":
    import sys
    file_str = (str(sys.argv[1]))
    #file_str = '/home/kolya/PycharmProjects/MyTests/test5.py'
    file = open(file_str, 'r')
    source_code_str = file.read()
    file.close()



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


    st = parser.suite(source_code_str)
    statements = parser.st2list(st, line_info=True, col_info=True)




    module = importlib.import_module('builtins')
    syms = inspect.getmembers(module)
    for sym in syms:
        if inspect.isfunction(sym[1]):
            GLOBAL_SYMBOL_LIST += [Function(sym[0],[],[])]
        elif inspect.isbuiltin(sym[1]):
            GLOBAL_SYMBOL_LIST += [Function(sym[0],[],[])]
        elif inspect.ismethod(sym[1]):
            pass
        elif inspect.isgeneratorfunction:
            #print(sym[0])
            GLOBAL_SYMBOL_LIST += [Function(sym[0],[],[])]
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
            GLOBAL_SYMBOL_LIST += [Class(sym[0],[])]
        else:
            print(sym[0])



















    findLocalSym(statements, GLOBAL_SYMBOL_LIST)


    for s in GLOBAL_SYMBOL_LIST:
        if type(s) == type(Function("",[],[])):
            s.body_parse(s.body,s.localSym)

    for err in ERROR_LIST:
        print(err.info)


