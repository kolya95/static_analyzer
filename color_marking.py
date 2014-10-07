from tokenize import generate_tokens, tokenize
import keyword
import token
from io import BytesIO
from kumir_constants import *
import parser


SECONDARY_KWD = ("in", "as", "is", "and", "or", "not", "pass", "break", "continue", "return", "else", "elif",
                 "if", "except", "finally", "try", "raise")
PRIMARY_KWD = ("def", "for", "class", "import", "from", "with", "global", "None", "while", "yield", "nonlocal", "lambda", "assert", "del")
#True, False -- отдельно, почему None не отдельно?

color_marks = [[]]
line_ranks = [0]

def set_color_marks_and_ranks(source_code_str):
    global color_marks
    global line_ranks
    color_marks = [[]]
    line_ranks = [0]
    i = 0
    tokens = tokenize(BytesIO(source_code_str.encode('utf-8')).readline)
    previous_tok_ecol = 0
    for tok in tokens:
        # tok[0] -- token type
        # tok[1] -- token string
        # tok[2] -- (srow, scol)
        # tok[3] -- (erow, ecol)
        # tok[4] -- "logical" line
        if tok[2] != tok[3] or tok[0] == token.DEDENT or tok[0] == token.NEWLINE:
            if tok[0] == token.NAME:
                color_marks[i].extend([LxTypeEmpty]*(tok[2][1] - previous_tok_ecol))
                if tok[1] in SECONDARY_KWD:
                    color_marks[i].extend([LxTypeSecondaryKwd]*len(tok[1]))
                elif tok[1] in PRIMARY_KWD:
                    color_marks[i].extend([LxTypePrimaryKwd]*len(tok[1]))
                elif tok[1] == "True":
                    color_marks[i].extend([LxConstBoolTrue]*len(tok[1]))
                elif tok[1] == "False":
                    color_marks[i].extend([LxConstBoolFalse]*len(tok[1]))
                else:
                    color_marks[i].extend([LxTypeName]*len(tok[1]))
                previous_tok_ecol = tok[3][1]
            elif tok[0] == token.STRING:
                color_marks[i].extend([LxTypeEmpty]*(tok[2][1] - previous_tok_ecol))
                color_marks[i].extend([LxConstLiteral]*len(tok[1]))
                previous_tok_ecol = tok[3][1]
            elif tok[0] == token.OP:
                color_marks[i].extend([LxTypeEmpty]*(tok[2][1] - previous_tok_ecol))
                color_marks[i].extend([LxTypeOperator]*len(tok[1]))
                previous_tok_ecol = tok[3][1]
            elif tok[0] == token.N_TOKENS: #comments
                color_marks[i].extend([LxTypeEmpty]*(tok[2][1] - previous_tok_ecol))
                color_marks[i].extend([LxTypeComment]*len(tok[1]))
                previous_tok_ecol = tok[3][1]
            elif tok[0] == token.INDENT:
                color_marks[i].extend([LxTypeEmpty]*len(tok[1]))
                line_ranks[len(line_ranks)-1] += 1
                previous_tok_ecol = tok[3][1]
            elif tok[0] == token.DEDENT:
                line_ranks[len(line_ranks)-1] -= 1
                #previous_tok_ecol = tok[3][1]
            elif tok[0] == token.NEWLINE or tok[0] == 55: #55 -- '\n'
                color_marks.append([])
                line_ranks.append(line_ranks[len(line_ranks)-1])
                i += 1
                previous_tok_ecol = 0
            elif tok[0] == token.NUMBER:
                color_marks[i].extend([LxConstInteger]*len(tok[1]))
                color_marks[i].extend([LxTypeEmpty]*(tok[2][1] - previous_tok_ecol))
                previous_tok_ecol = tok[3][1]
            elif tok[0] == token.COLON:
                color_marks[i].extend([LxConstInteger]*len(tok[1]))
                color_marks[i].extend([LxTypeEmpty]*(tok[2][1] - previous_tok_ecol))
                previous_tok_ecol = tok[3][1]
                line_ranks[len(line_ranks)-1] -= 1
            else:
                color_marks[i].extend([LxTypeEmpty]*(tok[2][1] - previous_tok_ecol))
                color_marks[i].extend([LxTypeEmpty]*len(tok[1]))
                previous_tok_ecol = tok[3][1]
    pair_line_ranks = []


    for i in range(len(line_ranks)):
        if i<len(line_ranks)-1:
            pair_line_ranks.append((0, line_ranks[i+1]-line_ranks[i]))
        else:
            pair_line_ranks.append((line_ranks[i], 0))
    line_ranks = []
    line_ranks.extend(pair_line_ranks)
    print(line_ranks)


def get_colors():
    global color_marks
    return color_marks

def get_ranks():
    global line_ranks
    return line_ranks


if __name__ == "__main__":
    file = open('/home/kolya/PycharmProjects/static_analyzer/MyTests/test4.py', 'r')
    file = open('/home/kolya/PycharmProjects/static_analyzer/color_marking.py', 'r')
    source_code_str = file.read()
    file.close()
    print(source_code_str)
    str_list = source_code_str.split('\n')
    set_color_marks_and_ranks(source_code_str)
    print( len(str_list) )
    print( len(color_marks) )
    for i in range(len(str_list)):
        if len(str_list[i])!=len(color_marks[i]):
            print("bad news..." + str(i))

            print(len(str_list[i]))
            print(len(color_marks[i]))


    print(get_colors())
    print(get_ranks())





