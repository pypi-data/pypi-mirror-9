#!/usr/bin/python

"""Safe user-supplied python expression evaluation."""

import ast
import sys

version = '0.3'


class SafeAST(ast.NodeVisitor):

    """AST-tree walker class."""

    allowed = {}

    def __init__(self, safenodes=None, addnodes=None):
        """create whitelist of allowed operations."""
        if safenodes is not None:
            self.allowed = safenodes
        else:
            # 123, 'asdf'
            values = ['Num', 'Str']
            # any expression
            expression = ['Expression']
            # == ...
            compare = ['Compare', 'Eq', 'NotEq', 'Gt', 'GtE', 'Lt', 'LtE']
            # variable name
            variables = ['Name', 'Load']
            binop = ['BinOp']
            arithmetics = ['Add', 'Sub']
            subscript = ['Subscript', 'Index']  # person['name']
            boolop = ['BoolOp', 'And', 'Or', 'UnaryOp', 'Not']  # True and True
            inop = ["In"]  # "aaa" in i['list']
            self.allowed = expression + values + compare + variables + binop + \
                arithmetics + subscript + boolop + inop

        if addnodes is not None:
            self.allowed = self.allowed + addnodes

    def generic_visit(self, node):
        """Check node, rais exception is node is not in whitelist."""
        if type(node).__name__ in self.allowed:
            ast.NodeVisitor.generic_visit(self, node)
        else:
            raise ValueError(
                "Operaton type {optype} is not allowed".format(
                    optype=type(node).__name__))


def evalidate(expression, safenodes=None, addnodes=None):
    """Validate expression.

    return node if it passes our checks
    or pass exception from SafeAST visit.
    """
    node = ast.parse(expression, '<usercode>', 'eval')

    v = SafeAST(safenodes, addnodes)
    v.visit(node)
    return node


def safeeval(src, context={}, safenodes=None, addnodes=None):
    """C-style simplified wrapper, eval() replacement."""
    try:
        node = evalidate(src, safenodes, addnodes)
    except Exception as e:
        return (False, "Validation error: "+e.__str__())

    try:
        code = compile(node, '<usercode>', 'eval')
    except Exception as e:
        return (False, "Compile error: "+e.__str__())

    try:
        wcontext = context.copy()
        result = eval(code, wcontext)
    except Exception as e:
        et, ev, erb = sys.exc_info()
        return False, "Runtime error ({}): {}".format(type(e).__name__, ev)

    return(True, result)


if __name__ == '__main__':

    books = [
        {
            'title': 'The Sirens of Titan',
            'author': 'Kurt Vonnegut',
            'stock': 10,
            'price': 9.71
        },
        {
            'title': 'Cat\'s Cradle',
            'author': 'Kurt Vonnegut',
            'stock': 2,
            'price': 4.23
        },
        {
            'title': 'Chapaev i Pustota',
            'author': 'Victor Pelevin',
            'stock': 0,
            'price': 21.33
        },
        {
            'title': 'Gone Girl',
            'author': 'Gillian Flynn',
            'stock': 5,
            'price': 8.97
        },
    ]

    src = 'stock>=5 and not price>9'

    for book in books:
        success, result = safeeval(src, book)
        if success:
            if result:
                print book
        else:
            print "ERR: ", result
