import sys
from collections import namedtuple


class ParsingOperand(object):
    '''
    This mixin-style class adds support for parsing operators::
        a & b  ==  And(a, b)
        a | b  ==  Or(a, b)
        a / b  ==  Alt(a, b, allow_trailer=True)
        a // b ==  Alt(a, b, allow_trailer=False)
        ~a     ==  Opt(a)
        a << b ==  Left(a, b)
        a >> b ==  Right(a, b)
        a ^ b  ==  Require(a, b)
        a * b  ==  Transform(a, b)
        a ** b ==  Bind(a, b)
    '''
    # MUST: use a table in the doc comment.
    def __and__(self, other): return And(self, other)
    def __rand__(self, other): return And(other, self)
    def __or__(self, other): return Or(self, other)
    def __ror__(self, other): return Or(other, self)
    def __div__(self, other): return Alt(self, other, allow_trailer=True)
    def __rdiv__(self, other): return Alt(other, self, allow_trailer=True)
    def __truediv__(self, other): return Alt(self, other, allow_trailer=True)
    def __rtruediv__(self, other): return Alt(other, self, allow_trailer=True)
    def __floordiv__(self, other): return Alt(self, other, allow_trailer=False)
    def __rfloordiv__(self, other): return Alt(other, self, allow_trailer=False)
    def __invert__(self): return Opt(self)
    def __lshift__(self, other): return Left(self, other)
    def __rlshift__(self, other): return Left(other, self)
    def __rshift__(self, other): return Right(self, other)
    def __rrshift__(self, other): return Right(other, self)
    def __mul__(self, other): return Transform(self, other)
    def __pow__(self, other): return Bind(self, other)
    def __xor__(self, other): return Require(self, other)


class ExpressionMetaClass(type, ParsingOperand):
    def __repr__(self):
        return self.__name__


class Struct(object):
    __metaclass__ = ExpressionMetaClass
    def parse(self): pass


class __Self(object):

    def __setattr__(self, name, value):
        if isinstance(value, tuple):
            fields, doc = value
            assert isinstance(doc, basestring)
        else:
            fields = value
            doc = None

        assert isinstance(fields, basestring)
        NT = namedtuple(name, fields)

        class ParsingExpression(ParsingOperand, NT):
            __metaclass__ = ExpressionMetaClass
            __doc__ = doc

            def __hash__(self):
                if not hasattr(self, '_hash'):
                    class_prefix = (id(ParsingExpression),)
                    try:
                        self._hash = hash(class_prefix + self)
                    except TypeError:
                        self._hash = id(self)
                return self._hash

            def __repr__(self):
                args = ', '.join(repr(i) for i in self)
                return '%s(%s)' % (name, args)

        ParsingExpression.__name__ = name
        setattr(sys.modules[__name__], name, ParsingExpression)


self = __Self()


self._Alt = 'element, separator, allow_trailer'


self.And = 'left, right', '''

    The expression ``left & right`` is equivalent to
    ``left >> Expect(right)``.

    It parses the left operand, but only returns the result if it's followed
    by the right operand.
'''


self.Any = '', '''

    Returns the next element of the input. Fails if the remaining input is
    empty. This class can be used as an expression directly, or it can be
    instantiated.

    Example 1::

        from sourcer import Any, parse

        # Parse the number one, then any value, then the number 3.
        # Note that the "Any" class does not need to be instantiated.
        goal = (1, Any, 3)
        ans = parse(goal, [1, 2, 3])
        assert ans == (1, 2, 3)

    Example 2::

        from sourcer import Any, parse

        # Try it again with a the string 'ok' in the middle position.
        # Also, this time try instantiating the "Any" object.
        goal = (1, Any(), 3)
        ans = parse(goal, [1, 'ok', 3])
        assert ans == (1, 'ok', 3)

    Example 3::

        from sourcer import Any, parse

        # Parse any character surrounded by parentheses,
        # discarding the parentheses.
        goal = '(' >> Any << ')'
        ans = parse(goal, '(a)')
        assert ans == 'a'
'''


self._Backtrack = 'count'


self.Bind = 'expression, function', '''

    ``Bind`` is used to create context-sensitive expressions.

    Example::

        from sourcer import *
        # Parse an integer.
        Int = Pattern(r'\d+') * int

        # Parse as many 'z' characters as the integer we just parsed.
        zs = Int ** (lambda count: 'z' * count)

        # Test it out on the digit '4' and then four 'z' characters.
        ans = parse(zs, '4zzzz')
        assert ans == 'zzzz'
'''


self.End = '', 'Matches the end of the input.'


self.Expect = 'expression'


self.Fail = '', 'Causes the parser to fail.'


self.ForwardRef = 'resolve'


self.Left = 'left, right'


self.List = 'element', '''

    Parse an expression zero or more times and return the results as a list.

    Example 1::

        from sourcer import *

        # Parse the string 'foo' zero or more times.
        foos = List('foo')

        # Try parsing 'foo' * 3.
        # Assert that we receive a list of three 'foo'.
        ans1 = parse(foos, 'foofoofoo')
        assert ans1 == ['foo', 'foo', 'foo']

        # Try parsing just one 'foo'.
        # Assert that we receive a list of one 'foo'.
        ans2 = parse(foos, 'foo')
        assert ans2 == ['foo']

        # Try parsing the empty string.
        # Assert that we receive the empty list.
        ans3 = parse(foos, '')
        assert ans3 == []

    Example 2::

        from sourcer import *

        # Parse a list of 'foo' followed by a list of 'bar'.
        foos = List('foo')
        bars = List('bar')
        goal = (foos, bars)

        # Try two 'foo' and two 'bar'.
        # Assert that we receive a pair of two lists,
        # one with two 'foo' and another with two 'bar'.
        ans1 = parse(goal, 'foofoobarbar')
        assert ans1 == (['foo', 'foo'], ['bar', 'bar'])

        # Try parsing just the string 'bar'.
        ans2 = parse(goal, 'bar')
        assert ans2 == ([], ['bar'])

        # Try parsing the empty string.
        # Assert that we receive a pair of two empty lists.
        ans3 = parse(goal, '')
        assert ans3 == ([], [])
'''


self.Literal = 'value'


self.Not = 'expression'


self.Opt = 'expression', '''

    The expression ``Opt(foo)`` is equivalent to ``foo | Return(None)``.
'''


self.Or = 'left, right', 'Ordered choice.'


self.Require = 'expression, predicate'


self.Return = 'value', '''
    Simply returns the provided value, without parsing any of the input.
    This can be useful as the last operand of an "Or" expression.

    Example::

        from sourcer import *
        Name = Pattern(r'\w+') | Return('User')
        Count = Pattern(r'\d+')
        ans = parse((Name, Count), '123')
        assert ans == ('User', '123')
'''


self.Right = 'left, right'


self.Some = 'element'


self.Start = '', 'Matches the beginning of the input.'


self.Term = 'value'


self.Transform = 'expression, function'


def Alt(element, separator, allow_trailer=True):
    return _Alt(element, separator, allow_trailer)


def Backtrack(count=1):
    '''

    Moves the current position back by some number of spaces. If the new
    position would be less than zero, then it fails and has no other effect.

    Example::

        from sourcer import *
        # (The ">>" operator means "discard the result from the left operand".)
        goal = Pattern(r'[a-z]+') >> Backtrack(1) >> 'o' >> Some('-')
        ans = parse(goal, 'foo---')
        assert ans == list('---')

    '''
    return _Backtrack(count)


def Where(test):
    return Any ^ test
