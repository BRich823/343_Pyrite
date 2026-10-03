import re
from struct import unpack
from token import Punctuator, Keyword, Identifier, Literal, TokenType, Token

class ScannerError(Exception):
    def __init__(self, message, loc):
        self.message = message
        self.line, self.col = loc

    def __str__(self):
        return f"{self.message} at line {self.line + 1}, column {self.col + 1}"


Error = ScannerError
    
class Scanner:
    def __init__(self, source):
        self.source = source if isinstance(source, list) else source.splitlines()
        self.tokens = []
        self.start = 0
        self.curr = 0
        self.line = 0

    # scans the entire source
    def scan(self):
        self.tokens = []
        self.start = 0
        self.curr = 0
        self.line = 0

        while self.line < len(self.source):
            line = self.source[self.line]
            while self.curr < len(line):
                if line[self.curr].isspace():
                    self.curr += 1
                    self.start = self.curr
                    continue

                token_type, lex = self.scan_lex()
                self.add_token(lex, token_type)

            self.add_token(None, 'eol')
            self.line += 1
            self.start = 0
            self.curr = 0

        self.add_token(None, 'eof')

    # scans the next token
    def scan_lex(self):
        line = self.source[self.line]
        if self.curr >= len(line):
            return 'eol', '\n'

        ch = line[self.curr]

        if ch in TokenType.Punctuator['singles']:
            self.curr += 1
            self.start = self.curr
            return 'punct', ch

        if ch in TokenType.Punctuator['doubles']:
            two_char = ch + (line[self.curr + 1] if self.curr + 1 < len(line) else '')
            if two_char in {'!=', '==', '>=', '<=', '//'}:
                self.curr += 2
                self.start = self.curr
                return 'punct', two_char
            self.curr += 1
            self.start = self.curr
            return 'punct', ch

        if ch.isalpha() or ch == '_':
            start = self.curr
            self.curr += 1
            while self.curr < len(line) and (line[self.curr].isalnum() or line[self.curr] == '_'):
                self.curr += 1
            lex = line[start:self.curr]
            self.start = self.curr
            if lex in TokenType.Keyword:
                return 'kw', lex
            return 'id', lex

        if ch.isdigit() or ch == '.':
            start = self.curr
            has_dot = ch == '.'
            self.curr += 1
            while self.curr < len(line):
                next_ch = line[self.curr]
                if next_ch.isdigit():
                    self.curr += 1
                    continue
                if next_ch == '.' and not has_dot:
                    has_dot = True
                    self.curr += 1
                    continue
                break
            lex = line[start:self.curr]
            self.start = self.curr
            return 'lit', lex

        if ch in ['"', "'"]:
            quote = ch
            start = self.curr
            self.curr += 1
            while self.curr < len(line) and line[self.curr] != quote:
                self.curr += 1
            if self.curr >= len(line):
                raise ScannerError('Unterminated string', (self.line, start))
            self.curr += 1
            lex = line[start:self.curr]
            self.start = self.curr
            return 'lit', lex

        raise ScannerError(f"Unexpected character {ch!r}", self.get_loc())

    def add_token(self, lex, type):
        loc = self.get_loc()
        typeToToken = {
            'lit': lambda: Literal(lex, loc),
            'id': lambda: Identifier(lex, loc),
            'kw': lambda: Keyword(lex, loc),
            'punct': lambda: Punctuator(lex, loc),
            'eof': lambda: Token(TokenType.Eof, None, loc, None),
            'eol': lambda: Token(TokenType.Eol, None, loc, None)
        }
        token = typeToToken.get(type)
        if token is None:
            return
        self.tokens.append(token())
        self.start = self.curr

    def set_source(self, source):
        self.source = source.splitlines()
        self.scan()

    def add_line(self, line):
        self.source.append(line)
        self.scan()

    def print_tokens(self):
        for t in self.tokens:
            print(t)

    def scan_until(self, cond):
        return ''

    def get_loc(self):
        return self.line, self.start