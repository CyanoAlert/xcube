import ast
from typing import Generator

import collections
import re
import warnings


def transpile_expr(expr: str, warn=False):
    """
    Transpiles a BEAM/SNAP expression into a numpy array expression.

    :param expr: The BEAM/SNAP expression
    :return The numpy array expression:
    """
    return _ExprTranspiler(expr, warn).transpile()


# noinspection PyMethodMayBeStatic
class _ExprTranspiler:
    """
    Transpiles a BEAM/SNAP expression into a numpy array expression.

    See https://greentreesnakes.readthedocs.io/en/latest/nodes.html#expressions
    """

    _KEYWORDS = {'in', 'not in', 'is', 'is not', 'and', 'or', 'not', 'True', 'False', 'None'}

    _OP_INFOS = {

        ast.Eq: ('==', 100, 'R'),
        ast.NotEq: ('!=', 100, 'R'),
        ast.Lt: ('<', 100, 'R'),
        ast.LtE: ('<=', 100, 'R'),
        ast.Gt: ('>', 100, 'R'),
        ast.GtE: ('>=', 100, 'R'),
        ast.Is: ('is', 100, 'R'),
        ast.IsNot: ('is not', 100, 'R'),
        ast.In: ('in', 100, 'R'),
        ast.NotIn: ('not in', 100, 'R'),

        ast.Or: ('or', 300, 'L'),
        ast.And: ('and', 400, 'L'),
        ast.Not: ('not', 500, None),

        ast.UAdd: ('+', 600, None),
        ast.USub: ('-', 600, None),

        ast.Add: ('+', 600, 'E'),
        ast.Sub: ('-', 600, 'L'),
        ast.Mult: ('*', 700, 'E'),
        ast.Div: ('/', 700, 'L'),
        ast.FloorDiv: ('//', 700, 'L'),
        ast.Mod: ('%', 800, 'L'),
        ast.Pow: ('**', 900, 'L'),
    }

    @classmethod
    def get_op_info(cls, op: ast.AST):
        return cls._OP_INFOS.get(type(op), (None, None, None))

    def __init__(self, expr: str, warn: bool):
        self.expr = expr
        self.warn = warn

    def transpile(self) -> str:
        return self._transpile(ast.parse(self.expr))

    def _transpile(self, node: ast.AST) -> str:
        if isinstance(node, ast.Module):
            return self._transpile(node.body[0])
        if isinstance(node, ast.Expr):
            return self._transpile(node.value)
        if isinstance(node, ast.Name):
            return self.transform_name(node)
        if isinstance(node, ast.NameConstant):
            return self.transform_name_constant(node)
        if isinstance(node, ast.Num):
            return self.transform_num(node)
        if isinstance(node, ast.Attribute):
            pat = self.transform_attribute(node.value, node.attr, node.ctx)
            x = self._transpile(node.value)
            return pat.format(x=x)
        if isinstance(node, ast.Call):
            pat = self.transform_call(node.func, node.args)
            xes = {'x%s' % i: self._transpile(node.args[i]) for i in range(len(node.args))}
            return pat.format(**xes)
        if isinstance(node, ast.UnaryOp):
            pat = self.transform_unary_op(node.op, node.operand)
            arg = self._transpile(node.operand)
            return pat.format(x=arg)
        if isinstance(node, ast.BinOp):
            pat = self.transform_bin_op(node.op, node.left, node.right)
            x = self._transpile(node.left)
            y = self._transpile(node.right)
            return pat.format(x=x, y=y)
        if isinstance(node, ast.BoolOp):
            pat = self.transform_bool_op(node.op, node.values)
            xes = {'x%s' % i: self._transpile(node.values[i]) for i in range(len(node.values))}
            return pat.format(**xes)
        if isinstance(node, ast.Compare):
            pat = self.transform_compare(node.left, node.ops, node.comparators)
            xes = {'x0': self._transpile(node.left)}
            xes.update({'x%s' % (i + 1): self._transpile(node.comparators[i]) for i in range(len(node.comparators))})
            return pat.format(**xes)
        raise ValueError('unrecognized expression node %s in "%s"' % node.__class__.__name__, self.expr)

    def transform_name(self, name: ast.Name):
        return name.id

    def transform_name_constant(self, node: ast.NameConstant):
        return repr(node.value)

    def transform_num(self, node: ast.Num):
        return str(node.n)

    def transform_call(self, func: ast.Name, args):
        args = ', '.join(['{x%d}' % i for i in range(len(args))])
        return "%s(%s)" % (self.transform_function_name(func), args)

    def transform_function_name(self, func: ast.Name):
        name = dict(min='fmin', max='fmax').get(func.id, func.id)
        return 'np.%s' % name

    # noinspection PyUnusedLocal
    def transform_attribute(self, value: ast.AST, attr: str, ctx):
        return "{x}.%s" % attr

    def transform_unary_op(self, op, operand):
        name, precedence, _ = self.get_op_info(op)

        x = '{x}'

        if name == 'not':
            return "np.logical_not(%s)" % x

        right_op = getattr(operand, 'op', None)
        if right_op:
            _, other_precedence, other_assoc = self.get_op_info(right_op)
            if other_precedence < precedence or other_precedence == precedence \
                    and other_assoc is not None:
                x = '({x})'

        if name in self._KEYWORDS:
            return "%s %s" % (name, x)
        else:
            return "%s%s" % (name, x)

    def transform_bin_op(self, op, left, right):
        name, precedence, assoc = _ExprTranspiler.get_op_info(op)

        x = '{x}'
        y = '{y}'

        if name == '**':
            return 'np.power(%s, %s)' % (x, y)

        left_op = getattr(left, 'op', None)
        right_op = getattr(right, 'op', None)

        if left_op:
            _, other_precedence, other_assoc = self.get_op_info(left_op)
            if other_precedence < precedence or other_precedence == precedence \
                    and assoc == 'R' and other_assoc is not None:
                x = '({x})'

        if right_op:
            _, other_precedence, other_assoc = self.get_op_info(right_op)
            if other_precedence < precedence or other_precedence == precedence \
                    and assoc == 'L' and other_assoc is not None:
                y = '({y})'

        return "%s %s %s" % (x, name, y)

    def transform_bool_op(self, op, values):
        name, precedence, assoc = _ExprTranspiler.get_op_info(op)

        if name == 'and' or name == 'or':
            expr = None
            for i in range(1, len(values)):
                expr = 'np.logical_%s(%s, {x%d})' % (name, '{x0}' if i == 1 else expr, i)
            return expr

        xes = []
        for i in range(len(values)):
            value = values[i]
            x = '{x%d}' % i
            other_op = getattr(value, 'op', None)
            if other_op:
                _, other_precedence, other_assoc = self.get_op_info(other_op)
                if i == 0 and other_precedence < precedence \
                        or i > 0 and other_precedence <= precedence:
                    x = '(%s)' % x
            xes.append(x)

        return (' %s ' % name).join(xes)

    # Compare(left, ops, comparators
    def transform_compare(self, left, ops, comparators):

        if len(ops) != 1:
            raise ValueError('expression "%s" uses an n-ary comparison, but only binary are supported' % self.expr)

        right = comparators[0]
        op = ops[0]
        name, precedence, assoc = _ExprTranspiler.get_op_info(op)

        x = '{x0}'
        y = '{x1}'

        if self._is_nan(right):
            nan_op = x
        elif self._is_nan(right):
            nan_op = y
        else:
            nan_op = None

        if nan_op:
            if self.warn:
                warnings.warn('Use of NaN as operand with comparison "%s" is ambiguous: "%s"' % (name, self.expr))
            if name == '==':
                return 'np.isnan(%s)' % nan_op
            if name == '!=':
                return 'np.logical_not(np.isnan(%s))' % nan_op

        left_op = getattr(left, 'op', None)
        if left_op:
            name, other_precedence, assoc = _ExprTranspiler.get_op_info(left_op)
            if other_precedence < precedence:
                x = '(%s)' % x

        right_op = getattr(right, 'op', None)
        if right_op:
            _, other_precedence, other_assoc = self.get_op_info(right_op)
            if other_precedence < precedence or other_precedence == precedence \
                    and assoc == 'L' and other_assoc is not None:
                y = '(%s)' % y

        return '%s %s %s' % (x, name, y)

    def _is_nan(self, node):
        return isinstance(node, ast.Name) and node.id == 'NaN'


Token = collections.namedtuple('Token', ['kind', 'value'])

_TOKEN_REGEX = None
_TOKEN_KEYWORDS = None


def get_token_regex():
    global _TOKEN_REGEX
    global _TOKEN_KEYWORDS
    if _TOKEN_REGEX is None:
        _TOKEN_KEYWORDS = {'AND', 'OR', 'NOT', 'true', 'false', 'NaN'}
        token_specification = [
            ('NUM', r'\d+(\.\d*)?'),  # Integer or decimal number
            ('ID', r'[_A-Za-z][_A-Za-z0-9]*'),  # Identifiers
            ('OP', r'\*\*|\!\=|\=\=|\>=|\<=|\<|\>|\+|\-|\*|\!|\%|\^|\.|\?|\:'),  # Operators
            ('PAR', r'[\(\)]'),  # Parentheses
            ('WHITE', r'[ \t\n\r]+'),  # Skip over spaces and tabs, new lines
            ('ERR', r'.'),  # Any other character
        ]
        _TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        _TOKEN_REGEX = re.compile(_TOKEN_REGEX)
    return _TOKEN_REGEX, _TOKEN_KEYWORDS


def tokenize_expr(code: str) -> Generator[Token, None, None]:
    token_regex, token_keywords = get_token_regex()
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'WHITE':
            pass
        elif kind == 'ERR':
            raise RuntimeError(f'{value!r} unexpected')
        else:
            if kind == 'ID' and value in token_keywords:
                kind = 'KW'
            yield Token(kind, value)
