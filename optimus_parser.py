from pyqubo import Binary, Num
from sympy import *

tokens = (
    'NAME','NUMBER',
    'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
    'LPAREN','RPAREN', 'MIN', 'COMMA', 'SUBJECT_TO', 'EQUALITYTOKEN', 'SOLVE', 'RUN_ON', 'COMMENT'
    )

# Tokens for simple symbols

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_COMMA = r'\,'

def t_COMMENT(t):
    r'//.*'
    t.lexer.skip(1)

def t_SUBJECT_TO(t):
	r'(subject\ to|st)'
	return t

def t_RUN_ON(t):
    r'(run\ on|run)'
    return t


def t_SOLVE(t):
    r'(solve|solver)'
    return t

def t_EQUALITYTOKEN(t):
    r'=='
    return t

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

def t_MIN(t):
    r'min'
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

# dictionary of variable names
names = { }

solve_parameters = {}

# dictionary of optimization formulations
optimization_formulations = []

def refresh_globals():
    global names, optimization_formulations, solve_parameters
    # dictionary of variable names
    names = { }

    solve_parameters = {}

    # dictionary of optimization formulations
    optimization_formulations = []    

def p_statement_assign(t):
    'statement : NAME EQUALS expression'
    names[t[1]] = t[3]

def p_statement_expr(t):
    'statement : expression'
    print(t[1])

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    if t[2] == '+'  : t[0] = t[1] + t[3]
    elif t[2] == '-': t[0] = t[1] - t[3]
    elif t[2] == '*': t[0] = t[1] * t[3]
    elif t[2] == '/': t[0] = t[1] / t[3]

# The first register is the return value.
def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]

def p_statement_optimization(t):
    '''statement : MIN expression
    			 | MIN expression COMMA expression
    			 | MIN expression COMMA expression COMMA expression
    '''
    optimization_formulations.append({"problem": t, "constraints": []})

def p_statement_subject_to(t):
    'statement : SUBJECT_TO expression EQUALITYTOKEN expression'
    optimization_formulations[-1]["constraints"].append(t)

def p_statement_run_on(t):
    '''statement : RUN_ON expression
                 | RUN_ON expression COMMA expression
                 | RUN_ON expression COMMA expression COMMA expression
    '''
    solve_parameters["run_on"] = []
    if len(t) == 3:
        solve_parameters["run_on"].append(t[2])
    if len(t) == 5:
        solve_parameters["run_on"].append(t[2])
        solve_parameters["run_on"].append(t[4])
    if len(t) == 7:
        solve_parameters["run_on"].append(t[2])
        solve_parameters["run_on"].append(t[4])
        solve_parameters["run_on"].append(t[6])


def p_statement_solve(t):
    '''statement : SOLVE NAME NAME
    '''
    if len(t) == 4:
        solve_parameters[t[2]] = t[3]
    elif len(t) == 5:
        solve_parameters[t[2]] = [t[3], t[4]]


def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    try:
        t[0] = names[t[1]]
    except LookupError:
        print("Symbol not found -- autogenerating", t[1])
        names[t[1]] = Binary(t[1])
        t[0] = names[t[1]]

def p_error(t):
    if t is None:
        pass
    else:
        print("Syntax error at '%s'" % t.value)

def parse_optimization_model(user_string, compiler_type="actual"):
    formulation = None
    constraints = []

    if compiler_type == "manual":

        for t in user_string.split("\n"):
            if t.startswith("min") or t.startswith("max"):
                formulation = t.split(" ")[1:]
                break
        for t in user_string.split("\n"):
            if t.startswith("subject to"):
                constraints.append(t.split(" ")[2:])

        return formulation, constraints

    if compiler_type == "actual":
        import ply.yacc as yacc
        parser = yacc.yacc()

        for ff in user_string.split("\n"):
            parser.parse(ff)

    objective_function = optimization_formulations[0]["problem"][2]
    constraints = []
    variables = names
    for i in range(len(optimization_formulations[0]["constraints"])):
        constraints.append([optimization_formulations[0]["constraints"][i][2], optimization_formulations[0]["constraints"][i][3], optimization_formulations[0]["constraints"][i][4]])

    return objective_function, constraints, variables, solve_parameters

if __name__ == "__main__":
    d = """
min 3*x*y + x*z + 4*z*y
subject to x+y+z == 1
subject to x-z == 1
solve prune dwave
run on dwave, rigetti, ibm
"""
    objective_function, constraints, variables, solve_parameters = parse_optimization_model(d.strip())
    import pdb; pdb.set_trace()
