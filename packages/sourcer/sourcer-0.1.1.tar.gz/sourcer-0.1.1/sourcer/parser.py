import inspect
from .terms import *


# Used to recognize regular expression objects.
RegexType = type(Regex(''))


def parse(term, source):
    whole = Left(term, End)
    ans = parse_prefix(whole, source)
    return ans.value


def parse_prefix(term, source):
    parser = Parser(source)
    return parser.run(term)


def tokenize_and_parse(tokenizer, term, source):
    tokens = tokenizer.run(source)
    return parse(term, tokens)


class Tokenizer(object):
    def __setattr__(self, name, value):
        assert name != '_Tokenizer__classes'
        if not hasattr(self, '_Tokenizer__classes'):
            object.__setattr__(self, '_Tokenizer__classes', [])
        value = TokenClass(name, value)
        self.__classes.append(value)
        object.__setattr__(self, name, value)

    def export(self, dst):
        dst.update(dict((cls.__name__, cls)
            for cls in self.__classes if not cls.skip))

    def run(self, source):
        main = List(Or(*self.__classes))
        ans = parse(main, source)
        return [t for t in ans if not t.skip]


def TokenClass(name, pattern):
    is_skipped = isinstance(pattern, Skip)
    if is_skipped:
        pattern = pattern.pattern
    if isinstance(pattern, basestring):
        pattern = Regex(pattern)

    class NewClass(Token):
        @staticmethod
        def parse(source, pos):
            if pos < len(source) and isinstance(source[pos], NewClass):
                yield ParseResult(source[pos], pos + 1)

            next = yield ParseStep(pattern, pos)
            if next is ParseFailure:
                yield ParseFailure

            match = next.value
            ans = NewClass(match.group(0))
            for k, v in match.groupdict().iteritems():
                setattr(ans, k, v)
            yield ParseResult(ans, next.pos)

    NewClass.__name__ = name
    NewClass.skip = is_skipped
    return NewClass


class Parser(object):
    def __init__(self, source):
        self.source = source
        self.memo = {}
        self.stack = []
        self.fieldmap = {}
        self.delegates = {}

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
            return self._parse_struct(term, pos)

        is_source_str = isinstance(self.source, basestring)

        if term == '' and is_source_str:
            return self._parse_nothing(term, pos)

        if isinstance(term, basestring) and is_source_str:
            return self._parse_text(term, pos)

        if isinstance(term, basestring):
            return self._parse_token(term, pos)

        if isinstance(term, RegexType):
            return self._parse_regex(term, pos)

        if isinstance(term, tuple):
            return self._parse_tuple(term, pos)
        else:
            return term.parse(self.source, pos)

    def _parse_nothing(self, term, pos):
        yield ParseResult(term, pos)

    def _parse_struct(self, term, pos):
        if term not in self.fieldmap:
            self.fieldmap[term] = struct_fields(term)
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
        if isinstance(next, Token) and next.content == term:
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


def _assoc_struct_builder(term, fields):
    names = [p[0] for p in fields]
    def build(left, op, right):
        ans = term.__new__(term)
        values = [left] + list(op) + [right]
        for name, value in zip(names, values):
            setattr(ans, name, value)
        return ans
    return build
