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
    
For advanced usage check out the documentation (http://pythonhosted.org//mathexpressions/).