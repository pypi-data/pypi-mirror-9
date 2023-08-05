from collections import namedtuple
import re


# This module raises this exception when it cannot parse an input sequence.
class ParseError(Exception): pass

# A singleton value used internally to indicate a parse failure.
ParseFailure = object()

# A tuple of (object, int). The object is the parse tree, and the int value
# is the index of the last item consumed by the parser, plus one. (So it's
# the index of the next item that the parser should consume.)
ParseResult = namedtuple('ParseResult', 'value, pos')

# Convenience function.
Regex = re.compile

# Special return value used to control the parser.
ParseStep = namedtuple('ParseStep', 'term, pos')


class ParsingOperand(object):
    '''
    This mixin-style class adds support for two parsing operators:
        a & b evaluates to And(a, b).
        a | b evaluates to Or(a, b).
    '''
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


# These classes add the "&" and "|" parsing operators.
class TermMetaClass(type, ParsingOperand): pass
class Term(ParsingOperand): __metaclass__ = TermMetaClass


class SimpleTerm(Term):
    '''Abstract base class for terms that consist of a single subterm.'''
    def __init__(self, term):
        self.term = term


def Alt(term, separator, allow_trailer=True):
    '''
    Parses a list of terms separated by a separator. Returns the elements
    in a normal list, and drops the separators.
    '''
    rest = List(Right(separator, term))
    tail = Opt(separator) if allow_trailer else None
    triple = (term, rest, tail)
    return Transform(Opt(triple), lambda t: [t[0]] + t[1] if t else [])


def And(left, right):
    return Left(left, Expect(right))


class Any(Term):
    '''
    Returns the next element of the input. Fails if the remaining input is
    empty. This class can be used as a term directly, or it can be
    instantiated.
    '''
    @staticmethod
    def parse(source, pos):
        yield (ParseFailure if pos >= len(source)
            else ParseResult(source[pos], pos + 1))


def AnyInst(*cls):
    return Where(lambda x: isinstance(x, cls))


class Bind(Term):
    def __init__(self, term, continuation):
        self.term = term
        self.continuation = continuation

    def parse(self, source, pos):
        arg = yield ParseStep(self.term, pos)
        if arg is ParseFailure:
            yield ParseFailure
        next = self.continuation(arg.value)
        ans = yield ParseStep(next, arg.pos)
        yield ans


class Expect(SimpleTerm):
    def parse(self, source, pos):
        ans = yield ParseStep(self.term, pos)
        yield ans if ans is ParseFailure else ParseResult(ans.value, pos)


class End(Term):
    @staticmethod
    def parse(source, pos):
        at_end = (pos == len(source))
        yield ParseResult(None, pos) if at_end else ParseFailure


class ForwardRef(SimpleTerm):
    def preparse(self):
        if not hasattr(self, 'cached_term'):
            self.cached_term = self.term()
        return self.cached_term


def Left(*args):
    return Transform(args, lambda ans: ans[0])


class List(SimpleTerm):
    def parse(self, source, pos):
        ans = []
        while True:
            next = yield ParseStep(self.term, pos)
            if next is ParseFailure:
                break
            pos = next.pos
            ans.append(next.value)
        yield ParseResult(ans, pos)


class Literal(Term):
    def __init__(self, value):
        self.value = value

    def parse(self, source, pos):
        is_match = (pos < len(source)) and source[pos] == self.value
        yield ParseResult(self.value, pos + 1) if is_match else ParseFailure


def Middle(left, middle, right):
    return Right(left, Left(middle, right))


class Not(SimpleTerm):
    def parse(self, source, pos):
        ans = yield ParseStep(self.term, pos)
        yield ParseResult(None, pos) if ans is ParseFailure else ParseFailure


def Opt(term):
    return Or(term, None)


class Or(Term):
    def __init__(self, *terms):
        self.terms = []
        # Flatten the list of terms.
        for term in terms:
            if isinstance(term, self.__class__):
                self.terms.extend(term.terms)
            else:
                self.terms.append(term)

    def parse(self, source, pos):
        for term in self.terms:
            ans = yield ParseStep(term, pos)
            if ans is not ParseFailure:
                yield ans
        yield ParseFailure


def Where(test):
    return Require(Any, test)


class Require(Term):
    def __init__(self, term, condition):
        self.term = term
        self.condition = condition

    def parse(self, source, pos):
        ans = yield ParseStep(self.term, pos)
        failed = (ans is ParseFailure) or not self.condition(ans.value)
        yield ParseFailure if failed else ans


def Right(*args):
    return Transform(args, lambda ans: ans[-1])


def Some(term):
    return Require(List(term), bool)


class Struct(object):
    __metaclass__ = TermMetaClass


def struct_fields(cls):
    ans = []
    class collect_fields(cls):
        def __setattr__(self, name, value):
            ans.append((name, value))
            cls.__setattr__(self, name, value)
    collect_fields()
    return ans


class LeftAssoc(Struct): pass
class RightAssoc(Struct): pass


class Token(object):
    __metaclass__ = TermMetaClass

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        name = self.__class__.__name__
        return '%s(%r)' % (name, self.content)


def AnyChar(pattern):
    assert isinstance(pattern, basestring)
    return Regex('[%s]' % re.escape(pattern))


def Content(token):
    return Transform(token, lambda token: token.content)


Skip = namedtuple('Skip', 'pattern')


class Transform(Term):
    def __init__(self, term, transform):
        self.term = term
        self.transform = transform

    def parse(self, source, pos):
        ans = yield ParseStep(self.term, pos)
        if ans is ParseFailure:
            yield ParseFailure
        else:
            value = self.transform(ans.value)
            yield ParseResult(value, ans.pos)


Pattern = lambda x: Transform(Regex(x), lambda m: m.group(0))
Verbose = lambda x: Regex(x, re.VERBOSE)


# Utility function to create a tuple from a variable number of arguments.
pack_tuple = (lambda *args: args)


def ReduceLeft(left, op, right, transform=pack_tuple):
    term = (left, Some((op, right)))
    assoc = lambda first, rest: transform(first, *rest)
    xform = lambda pair: reduce(assoc, pair[1], pair[0])
    return Transform(term, xform)


def ReduceRight(left, op, right, transform=pack_tuple):
    term = (Some((left, op)), right)
    assoc = lambda prev, next: transform(next[0], next[1], prev)
    xform = lambda pair: reduce(assoc, reversed(pair[0]), pair[1])
    return Transform(term, xform)


Operation = namedtuple('Operation', 'left, operator, right')


class OperatorRow(object):
    has_left = True
    has_right = True
    reduce_left = True

    def __init__(self, *operators):
        self.operator = operators

    def build(self, Operand):
        left = Operand if self.has_left else None
        right = Operand if self.has_right else None
        method = ReduceLeft if self.reduce_left else ReduceRight
        return method(left, Or(*self.operator), right, Operation)


class InfixLeft(OperatorRow): reduce_left = True
class InfixRight(OperatorRow): reduce_left = False


class Prefix(OperatorRow):
    has_left = False
    reduce_left = False


class Postfix(OperatorRow):
    has_right = False
    reduce_left = True


def OperatorPrecedence(*rows):
    ext = lambda Operand, row: row.build(Operand) | Operand
    return reduce(ext, rows)
