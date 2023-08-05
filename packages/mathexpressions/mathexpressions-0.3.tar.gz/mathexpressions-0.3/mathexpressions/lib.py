__author__ = 'Noah Peeters'

import math

const_names = ['pi', 'e']
const_values = [math.pi, math.e]
const_latex = ['\pi', 'e']

float_chars = [str(x) for x in range(10)]
float_chars.append('.')

operators = ['+', '-', '*', '/', '^']
operators_priorities = [0, 0, 1, 1, 2]
operators_latex = ['%s+%s', '%s-%s', '%s*%s', '\\frac{%s}{%s}', '%s^{%s}']

max_priority = 2


def use_operator(o, para1, para2):
    if o == '+':
        return para1 + para2
    elif o == '-':
        return para1 - para2
    elif o == '*':
        return para1 * para2
    elif o == '/':
        return para1 / para2
    elif o == '^':
        return math.pow(para1, para2)


def latex_operator(o, para1, para2):
    index = operators.index(o)
    return operators_latex[index] % (para1, para2)


def get_const_latex(name):
    if name in const_names:
        return const_latex[const_names.index(name)]
    else:
        return name


def get_priority(p):
    return operators_priorities[operators.index(p.name)]


functions = ['sin', 'pow']
functions_latex = ['\sin(%s)', '%s^{%s}']


def use_function(name, para):
    if name == 'sin':
        return math.sin(para[0])
    elif name == 'pow':
        return pow(para[0], para[1])


def get_function_latex(name, para):
    return functions_latex[functions.index(name)] % tuple(para)