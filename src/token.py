class TokenType:
    # (pyr, py)
    Literal = {'str': 'STR', 'int': 'INT', 'bool': 'BOOL'}
    Identifier = 'IDENTIFIER'
    Keywords = {
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
    Punctuators = {
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
    
if __name__ == "__main__":
    # test token class
    t = Token(TokenType.Literal['int'], '123', (1, 1))
    print(t)
    lex = ')'
    print(Token(TokenType.Punctuators['singles'][lex], lex, (1, 1)))