from tokenize import generate_tokens, tokenize
import keyword
import token
from io import BytesIO
import parser


file = open('/home/kolya/PycharmProjects/MyTests/test4.py', 'r')
source_code_str = file.read()
file.close()

try:
   a = compile(source_code_str, '', '')
except IndentationError as error:
   message = {'type': 'F',
                'row': -1,
                'column': -1,
                'text': str(error)}
   print(message)
   exit()




numOfLines = 1
tokList = []
for tok in tokenize(BytesIO(source_code_str.encode('utf-8')).readline):
    tokList = tokList + [tok]
    print(tok)
    if tok[0] == token.NEWLINE:
        numOfLines += 1





# typeLex -- стандартные из TokenInfo, для ключевых слов будем использовать 100

CONST_KW_INDEX = 100;
CONST_SPACE_INDEX = 101;
class Lexeme:
    def __init__(self, typeLex,str, startIndex, endIndex, color):
        self.typeLex = typeLex
        self.str = str
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.color = color

program = [[] for i in range(numOfLines)]
i = 0
for tok in tokList:
    if tok[1] in keyword.kwlist:
        program[i] = program[i] + [Lexeme(CONST_KW_INDEX,tok[1],tok[2][1],tok[3][1],'K')]
    elif i<len(program):
        if len(program[i])>=1:
            if program[i][len(program[i])-1].endIndex != tok[2][1]:
                temp = program[i][len(program[i])-1].endIndex
                program[i] = program[i] + [Lexeme(CONST_SPACE_INDEX,' ',temp,tok[2][1],'E'*(tok[2][1]-temp))]
        if tok[0] == token.NAME:
            program[i] = program[i] + [Lexeme(tok[0],tok[1],tok[2][1],tok[3][1],'N'*(tok[3][1]-tok[2][1]))]
        elif tok[0] == 54: # почему-то отсутствует token.COMMENT
            program[i] = program[i] + [Lexeme(tok[0],tok[1],tok[2][1],tok[3][1],'C'*(tok[3][1]-tok[2][1]))]
        elif tok[0] == token.NEWLINE:
            program[i] = program[i] + [Lexeme(tok[0],tok[1],tok[2][1],tok[3][1],'L'*(tok[3][1]-tok[2][1]))]
            i += 1
        elif tok[0] == token.OP:
            program[i] = program[i] + [Lexeme(tok[0],tok[1],tok[2][1],tok[3][1],'O'*(tok[3][1]-tok[2][1]))]
        elif tok[0] == token.STRING:
            program[i] = program[i] + [Lexeme(tok[0],tok[1],tok[2][1],tok[3][1],'S'*(len(tok[1])))]
        else:
            program[i] = program[i] + [Lexeme(tok[0],tok[1],tok[2][1],tok[3][1],'X'*(tok[3][1]-tok[2][1]))]



class LINE:
    def __init__(self, statements, relativeIndent = 0 ):
        self.statements = statements
        self.relativeIndent = relativeIndent
for lex in program:
    print(lex)

colorMarks = [[] for i in range(numOfLines)]

lines = []
counter = 0

i = 0
for k in range(len(program)):
    while i<len(program[k]) and program[k][i].typeLex == token.DEDENT:
        counter -= 1
        i+=1
    while i<len(program[k]) and program[k][i].typeLex == token.INDENT:
        counter += 1
        i+=1
    lines += [LINE(program[k],counter)]
    print(counter)
    counter = 0
    i = 0
    for j in program[k]:
        colorMarks[k] += [j.color]

print(colorMarks)


st = parser.suite(source_code_str)
statements = parser.st2list(st, line_info=True, col_info=True)
print(statements)