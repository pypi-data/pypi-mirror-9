import inspect
from .terms import *
from .precedence import *


def parse(term, source):
    whole = Left(term, End)
    ans = parse_prefix(whole, source)
    return ans.value


def parse_prefix(term, source):
    parser = Parser(source)
    return parser.run(term)


class Parser(object):
    def __init__(self, source):
        self.source = source
        self.memo = {}
        self.stack = []
        self.fieldmap = {}
        self.delegates = {}
        self.bindings = [(None, {})]
        is_str = isinstance(source, basestring)
        self._parse_string = self._parse_text if is_str else self._parse_token

    def run(self, term):
        ans = self._start(term, 0)
        while self.stack:
            top = self.stack[-1][-1]
            ans = top.send(ans)
            if isinstance(ans, ParseStep):
                ans = self._start(ans.term, ans.pos)
            else:
                key = self.stack.pop()[0]
                self.memo[key] = ans
                self._pop_scope(key[0])
        if ans is ParseFailure:
            raise ParseError()
        else:
            return ans

    def _start(self, term, pos):
        while isinstance(term, ForwardRef):
            term = term.preparse()
        key = (term, pos)
        if key in self.memo:
            return self.memo[key]
        self.memo[key] = ParseFailure
        generator = self._parse(term, pos)
        self.stack.append((key, generator))
        return None

    def _parse(self, term, pos):
        if term is None:
            return self._parse_nothing(term, pos)

        if inspect.isclass(term) and issubclass(term, Struct):
            self._push_scope(term)
            return self._parse_struct(term, pos)

        if isinstance(term, tuple):
            self._push_scope(term)
            return self._parse_tuple(term, pos)

        if isinstance(term, basestring):
            return self._parse_string(term, pos)

        if hasattr(term, 'parse'):
            return term.parse(self.source, pos)

        if hasattr(term, 'match'):
            return self._parse_regex(term, pos)

        if isinstance(term, Let):
            return self._parse_let(term, pos)

        if isinstance(term, Get):
            return self._parse_get(term, pos)

        if inspect.isfunction(term):
            return self._parse_dependent_term(term, pos)

        else:
            return Literal(term).parse(self.source, pos)

    def _parse_nothing(self, term, pos):
        yield ParseResult(term, pos)

    def _parse_struct(self, term, pos):
        if term not in self.fieldmap:
            self.fieldmap[term] = _struct_fields(term)
        if issubclass(term, (LeftAssoc, RightAssoc)):
            return self._parse_assoc_struct(term, pos)
        else:
            return self._parse_simple_struct(term, pos)

    def _parse_simple_struct(self, term, pos):
        ans = term.__new__(term)
        for field, value in self.fieldmap[term]:
            next = yield ParseStep(value, pos)
            if next is ParseFailure:
                yield ParseFailure
            setattr(ans, field, next.value)
            pos = next.pos
        yield ParseResult(ans, pos)

    def _parse_assoc_struct(self, term, pos):
        if term not in self.delegates:
            fields = self.fieldmap[term]
            first = fields[0][-1]
            middle = tuple(p[-1] for p in fields[1:-1])
            last = fields[-1][-1]
            build = _assoc_struct_builder(term, fields)
            is_left = issubclass(term, LeftAssoc)
            cls = ReduceLeft if is_left else ReduceRight
            self.delegates[term] = cls(first, middle, last, build)
        return self._parse(self.delegates[term], pos)

    def _parse_regex(self, term, pos):
        if not isinstance(self.source, basestring):
            yield ParseFailure
        match = term.match(self.source, pos)
        yield ParseResult(match, match.end()) if match else ParseFailure

    def _parse_text(self, term, pos):
        end = pos + len(term)
        part = self.source[pos : end]
        yield ParseResult(term, end) if part == term else ParseFailure

    def _parse_token(self, term, pos):
        if pos >= len(self.source):
            yield ParseFailure
        next = self.source[pos]
        if getattr(next, 'content') == term:
            yield ParseResult(term, pos + 1)
        else:
            yield ParseFailure

    def _parse_tuple(self, term, pos):
        ans = []
        for item in term:
            next = yield ParseStep(item, pos)
            if next is ParseFailure:
                yield ParseFailure
            ans.append(next.value)
            pos = next.pos
        yield ParseResult(tuple(ans), pos)

    def _parse_let(self, term, pos):
        ans = yield ParseStep(term.term, pos)
        if ans is not ParseFailure:
            self.bindings[-1][-1][term.name] = ans.value
        yield ans

    def _parse_get(self, term, pos):
        name = term.name
        for _, scope in reversed(self.bindings):
            if name in scope:
                yield ParseResult(scope[name], pos)
        ans = term.default
        yield ans if ans is ParseFailure else ParseResult(ans, pos)

    def _parse_dependent_term(self, term, pos):
        (args, varargs, keywords, defaults) = inspect.getargspec(term)
        assert not varargs and not keywords
        assert len(args) == 1
        defaults = defaults or ()
        ans = Bind(Get(args[0], *defaults), term)
        return self._parse(ans, pos)

    def _push_scope(self, term):
        self.bindings.append((term, {}))

    def _pop_scope(self, term):
        if term is self.bindings[-1][0]:
            self.bindings.pop()


def _assoc_struct_builder(term, fields):
    names = [p[0] for p in fields]
    def build(left, op, right):
        ans = term.__new__(term)
        values = [left] + list(op) + [right]
        for name, value in zip(names, values):
            setattr(ans, name, value)
        return ans
    return build


def _struct_fields(cls):
    ans = []
    class collect_fields(cls):
        def __setattr__(self, name, value):
            ans.append((name, value))
            cls.__setattr__(self, name, value)
    collect_fields()
    return ans
