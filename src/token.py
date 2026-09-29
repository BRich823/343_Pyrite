class TokenType:
    IDENTIFIER = 0
    LITERAL = 1
    KEYWORD = 2
    OPERATOR = 3
    PUNCTUATOR = 4

class Token:
    def __init__(self, type, value=None, lex=None, loc=None):
        self.type = type
        self.value = value
        self.lex = lex
        self.loc = loc # tuple of (line, col)

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, {repr(self.lex)}, {repr(self.loc)})'