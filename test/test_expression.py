import unittest

from xcube.expression import transpile_expr


class TranspileExprTest(unittest.TestCase):
    def test_unary(self):
        self.assertEqual(transpile_expr('-(-+(-x))'), '--+-x')
        self.assertEqual(transpile_expr('-((a-b)-c)'), '-(a - b - c)')
        self.assertEqual(transpile_expr('not x'), 'np.logical_not(x)')
        self.assertEqual(transpile_expr('not -x'), 'np.logical_not(-x)')
        self.assertEqual(transpile_expr('not not x'), 'np.logical_not(np.logical_not(x))')

    def test_binary(self):
        self.assertEqual(transpile_expr('a-b-c-d'), 'a - b - c - d')
        self.assertEqual(transpile_expr('(a-b)-c-d'), 'a - b - c - d')
        self.assertEqual(transpile_expr('(a-b-c)-d'), 'a - b - c - d')
        self.assertEqual(transpile_expr('a-(b-c)-d'), 'a - (b - c) - d')
        self.assertEqual(transpile_expr('a-(b-c-d)'), 'a - (b - c - d)')
        self.assertEqual(transpile_expr('a-b-(c-d)'), 'a - b - (c - d)')
        self.assertEqual(transpile_expr('a-(b-(c-d))'), 'a - (b - (c - d))')
        self.assertEqual(transpile_expr('(a-(b-c))-d'), 'a - (b - c) - d')

        self.assertEqual(transpile_expr('a----b'), 'a - ---b')
        self.assertEqual(transpile_expr('---a-b'), '---a - b')

        self.assertEqual(transpile_expr('a*b+c/d'), 'a * b + c / d')
        self.assertEqual(transpile_expr('a+b*c-d'), 'a + b * c - d')
        self.assertEqual(transpile_expr('(a+b)*(c-d)'), '(a + b) * (c - d)')

        self.assertEqual(transpile_expr('a ** b'), 'np.power(a, b)')

    def test_bool(self):
        self.assertEqual(transpile_expr('a and b and c'), 'np.logical_and(np.logical_and(a, b), c)')
        self.assertEqual(transpile_expr('(a and b) and c'), 'np.logical_and(np.logical_and(a, b), c)')
        self.assertEqual(transpile_expr('a and (b and c)'), 'np.logical_and(a, np.logical_and(b, c))')
        self.assertEqual(transpile_expr('(a or b) and not (c or not d)'),
                         'np.logical_and(np.logical_or(a, b), np.logical_not(np.logical_or(c, np.logical_not(d))))')

        self.assertEqual(transpile_expr('a and b or c and d'),
                         'np.logical_or(np.logical_and(a, b), np.logical_and(c, d))')
        self.assertEqual(transpile_expr('a or b and c or d'),
                         'np.logical_or(np.logical_or(a, np.logical_and(b, c)), d)')
        self.assertEqual(transpile_expr('(a or b) and (c or d)'),
                         'np.logical_and(np.logical_or(a, b), np.logical_or(c, d))')

    def test_compare(self):
        self.assertEqual(transpile_expr('a < 2'), 'a < 2')
        self.assertEqual(transpile_expr('a != 2'), 'a != 2')
        self.assertEqual(transpile_expr('a == NaN'), 'np.isnan(a)')
        self.assertEqual(transpile_expr('a != NaN'), 'np.logical_not(np.isnan(a))')
        self.assertEqual(transpile_expr('a is not Null'), 'a is not Null')
        self.assertEqual(transpile_expr('a in data'), 'a in data')

        with self.assertRaises(ValueError) as cm:
            transpile_expr('a >= 2 == b')
        self.assertEqual(str(cm.exception),
                         'expression "a >= 2 == b" uses an n-ary comparison, but only binary are supported')

        with self.assertRaises(ValueError) as cm:
            transpile_expr('0 < x <= 1')
        self.assertEqual(str(cm.exception),
                         'expression "0 < x <= 1" uses an n-ary comparison, but only binary are supported')

    def test_attributes(self):
        self.assertEqual(transpile_expr('a.b'), 'a.b')

    def test_functions(self):
        self.assertEqual(transpile_expr('sin(x)'), 'np.sin(x)')
        self.assertEqual(transpile_expr('min(x, y)'), 'np.fmin(x, y)')
        self.assertEqual(transpile_expr('max(x, y)'), 'np.fmax(x, y)')

    def test_conditional(self):
        # The following conditional expr looks wrong but this is how it looks like after translating
        # from SNAP expression 'a >= 0.0 ? a : NaN'
        self.assertEqual(transpile_expr('a >= 0.0 if a else NaN'),
                         'np.where(a >= 0.0, a, NaN)')
        self.assertEqual(transpile_expr('a >= 0.0 if a else b >= 0.0 if b else NaN'),
                         'np.where(a >= 0.0, a, np.where(b >= 0.0, b, NaN))')

    def test_mixed(self):
        self.assertEqual(transpile_expr('a+sin(x + 2.8)'),
                         'a + np.sin(x + 2.8)')
        self.assertEqual(transpile_expr('a+max(1, sin(x+2.8), x**0.5)'),
                         'a + np.fmax(1, np.sin(x + 2.8), np.power(x, 0.5))')


