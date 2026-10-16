from token import TokenType
from ast import Binary, Unary, Grouping, Literal


class ParseError(Exception):
    def __init__(self, message, token):
        self.message = message
        self.token = token

    def __str__(self):
        loc = self.token.loc if self.token else None
        if loc:
            return f"{self.message} at line {loc[0] + 1}, column {loc[1] + 1}"
        return self.message


class Parser:
    def __init__(self, tokens):
        # Strip EOL tokens; keep EOF
        self.tokens = [t for t in tokens if t.type != TokenType.Eol]
        self.curr = 0


    def parse(self):
        expr = self.expression()
        self.consume(TokenType.Eof, "Expected end of expression")
        return expr

    # --- grammar rules (lowest to highest precedence) ---

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()
        while self.match('EQUAL_EQUAL', 'BANG_EQUAL'):
            op = self.previous()
            expr = Binary(expr, op, self.comparison())
        return expr

    def comparison(self):
        expr = self.term()
        while self.match('GREATER', 'GREATER_EQUAL', 'LESS', 'LESS_EQUAL'):
            op = self.previous()
            expr = Binary(expr, op, self.term())
        return expr

    def term(self):
        expr = self.factor()
        while self.match('PLUS', 'MINUS'):
            op = self.previous()
            expr = Binary(expr, op, self.factor())
        return expr

    def factor(self):
        expr = self.unary()
        while self.match('STAR', 'SLASH'):
            op = self.previous()
            expr = Binary(expr, op, self.unary())
        return expr

    def unary(self):
        if self.match('BANG', 'MINUS'):
            op = self.previous()
            return Unary(op, self.unary())
        return self.primary()

    def primary(self):
        if self.match('INT', 'FLOAT', 'STR'):
            return Literal(self.previous().value)

        if self.match('TRUE'):
            return Literal(True)

        if self.match('FALSE'):
            return Literal(False)

        if self.match('NULL'):
            return Literal(None)

        if self.match('LPAREN'):
            expr = self.expression()
            self.consume('RPAREN', "Expected ')' after expression")
            return Grouping(expr)

        raise ParseError("Expected expression", self.peek())

    # --- helpers ---

    def match(self, *types):
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, type):
        return not self.is_at_end() and self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.curr += 1
        return self.previous()

    def consume(self, type, message):
        if self.peek().type == type:
            return self.advance()
        raise ParseError(message, self.peek())

    def is_at_end(self):
        return self.peek().type == TokenType.Eof

    def peek(self):
        return self.tokens[self.curr]

    def previous(self):
        return self.tokens[self.curr - 1]
