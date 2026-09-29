from token import Token, TokenType

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.curr = 0
        self.line = 0
        self.punctuation = '[]{}();,.+-*'
    
    # scans the entire source
    def scan(self):
        # check for EOF
        while self.line < len(self.source):
            self.scan_next()
            # set type to t, value to v, lex to start:curr, loc to self.start
            self.tokens.append(Token(t, v, self.source[self.line][self.start:self.curr + 1], self.start))
            self.start = self.curr
        self.tokens.append(Token(TokenType.EOF, None, None, None))
    # scans the next token
    def scan_next(self): # returns type and value
        self.curr += 1
        # check for EOL, line++
        # check for each type of token
