PyMathExpressions
-----------------

Python library for parsing and solving math expressions.

Simple example:

    >>> import mathexpressions
    >>> parser = mathexpressions.Parser()
    >>> parser.add_var('x', 3)
    >>> parser.parse_function('x^2')
    >>> print(parser.calc_function())
    9
    >>> parser.edit_var('x', 4)
    >>> parser.parse_function('x^2')
    16
    
For advanced usage check the example.py (https://github.com/NoahPeeters/pymathexpressions/blob/master/example.py) out.
A documentation is comming soon.