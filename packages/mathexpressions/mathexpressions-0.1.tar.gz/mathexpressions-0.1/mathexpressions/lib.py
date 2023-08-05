__author__ = 'Noah Peeters'

import math

constNames = ['pi', 'e']
constValues = [math.pi, math.e]

floatChars = [str(x) for x in range(10)]
floatChars.append('.')

operators = ['+', '-', '*', '/', '^']
operator_priorities = [0, 0, 1, 1, 2]
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


def get_priority(p):
    return operator_priorities[operators.index(p.name)]


functions = ['sin', 'pow']


def use_function(name, para):
    if name == 'sin':
        return math.sin(para[0])
    elif name == 'pow':
        return pow(para[0], para[1])