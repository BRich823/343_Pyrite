class TokenType:
    # (pyr, py)
    Literal = {'str': 'STR', 'int': 'INT', 'float': 'FLOAT'}
    Identifier = 'IDENTIFIER'
    Keyword = {
        "and": "AND",
        "class": "CLASS",
        "else": "ELSE",
        "false": "FALSE",
        "for": "FOR",
        "fun": "FUN",
        "if": "IF",
        "nil": "NULL",
        "or": "OR",
        "print": "PRINT",
        "return": "RETURN",
        "super": "SUPER",
        "this": "THIS",
        "true": "TRUE",
        "var": "VAR",
        "while": "WHILE",
    }
    Punctuator = {
        'singles': {
            '(': "LPAREN",
            ')': "RPAREN",
            '[': "LBRACK",
            ']': "RBRACK",
            '{': "LBRACE",
            '}': "RBRACE",
            ',': "COMMA",
            ':': "COLON",
            ';': "SEMICOLON",
            '.': "DOT",
            '+': "PLUS",
            '-': "MINUS",
            '*': "STAR",
            },
        'doubles': {
            '!': "BANG",
            '!=': "BANG_EQUAL",
            '=': "EQUAL",
            '==': "EQUAL_EQUAL",
            '>': "GREATER",
            '>=': "GREATER_EQUAL",
            '<': "LESS",
            '<=': "LESS_EQUAL",
            '/': "SLASH",
            '//': "SLASH_SLASH",
            }    
        }
    Eof = 'EOF'
    Eol = 'EOL'
    
class Token:
    def __init__(self, type, lex=None, loc=None, value=None):
        self.type = type
        self.lex = lex
        self.loc = loc # tuple of (line, col)
        self.value = value if value else self.__convert__()
        
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, {repr(self.lex)}, {repr(self.loc)})'

    def __convert__(self):
        # token type to value/better type
        pass

class Literal(Token):
    def __init__(self, lex, loc):
        # try to convert to int/float/str
        try:
            v = int(lex)
            t = 'int'
        except ValueError:
            try:
                v = float(lex)
                t = 'float'
            except ValueError:
                v = lex
                t = 'str'
        super().__init__(TokenType.Literal[t], lex, loc, v)
    
class Identifier(Token):
    def __init__(self, lex, loc):
        super().__init__(TokenType.Identifier, lex, loc)

class Keyword(Token):
    def __init__(self, lex, loc):
        super().__init__(TokenType.Keyword[lex], lex, loc)

class Punctuator(Token):
    def __init__(self, lex, loc):
        i = 'singles' if lex in TokenType.Punctuator['singles'] else 'doubles'
        super().__init__(TokenType.Punctuator[i][lex], lex, loc)
                
if __name__ == "__main__":
    # test token class
    t = Literal('123.0', (1, 1))
    print(t)
    lex = ')'
    print(Punctuator(lex, (1, 1)))