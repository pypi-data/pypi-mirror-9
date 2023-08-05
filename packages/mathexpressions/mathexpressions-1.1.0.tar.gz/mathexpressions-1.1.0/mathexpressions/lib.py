__author__ = 'Noah Peeters'

import math

const = {
    'pi': [math.pi, '\pi'],
    'e': [math.e, 'e']
}

float_chars = [str(x) for x in range(10)]
float_chars.append('.')

operators = ['+', '-', '*', '/', '^', '%', '=']
operators_priorities = [0, 0, 1, 1, 2, 1, 0]
operators_latex = ['%s+%s', '%s-%s', '%s*%s', '\\frac{%s}{%s}', '%s^{%s}', '%s\\mod%s', '%s=%s']

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
    elif o == '%':
        return math.pow(para1, para2)
    elif o == '=':
        return None


def latex_operator(o, para1, para2):
    index = operators.index(o)
    return operators_latex[index] % (para1, para2)


def get_priority(p):
    return operators_priorities[operators.index(p.name)]


def is_number(name):
    if len(name) == 0:
        return False
    for i in name:
        if i not in float_chars:
            return False
    return True


functions = {
    'acos': '\\arccos(%s)',
    'acosh': None,
    'asin': '\\arcsin(%s)',
    'asinh': None,
    'atan': '\\arctan(%s)',
    'atan2': None,
    'atanh': None,
    'ceil': None,
    'copysign': None,
    'cos': '\\cos(%s)',
    'cosh': '\\cosh(%s)',
    'degrees': None,
    'erf': None,
    'erfc': None,
    'exp': 'e^{%s}',
    'expm1': 'e^{%s}-1',
    'abs': '|%s|',
    'factorial': '%s!',
    'floor': None,
    'fmod': '%s\\mod%s',
    'gamma': None,
    'hypot': '\\sqrt(%s^{2}+%s^{2})',
    'ldexp': None,
    'lgamma': None,
    'log': '\\log(%s)',
    'log10': '\\log_10(%s)',
    'logn': None,  # latex support
    'pow': '%s^{%s}',
    'radians': None,
    'round': None,
    'roundn': None,
    'sin': '\\sin(%s)',
    'sinh': '\\sinh(%s)',
    'sqrt': '\\sqrt(%s)',
    'tan': '\\tan(%s)',
    'tanh': '\\tanh(%s)'
}


def use_function(name, para):
    if name == 'logn':
        return math.log(para[0], para[1])
    elif name == 'round':
        return round(para[0])
    elif name == 'roundn':
        return round(para[0], para[1])
    elif name == 'abs':
        return math.fabs(para[0])
    else:
        return getattr(math, name)(*para)


def get_function_latex(name, para):
    if name == 'logn':
        return '\\log_%s(%s)' % (para[1], para[0])
    else:
        return functions[name] % tuple(para)