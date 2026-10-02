import re
from token import Token, TokenType

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.curr = 0
        self.line = 0
    
    # scans the entire source
    def scan(self):
        # check for EOF
        while self.line < len(self.source):
            lex = self.scan_lex()
            self.start = self.curr
        self.tokens.append(Token(TokenType.EOF, None, None, None))
    # scans the next token
    def scan_lex(self): # returns lex
        self.curr += 1
        lex = self.source[self.line][self.start:self.curr]
        if lex in self.punctuation:
            return lex
        # check identifiers and keywords
        elif re.search(r'[a-zA-Z_][a-zA-Z0-9_]*', lex):
            pass
