from token import TokenType
from ast import Binary, Unary, Grouping, Literal
from evaluator import Statement


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
        self.errors = []


    def parse(self):
        expr = self.expression()
        self.consume(TokenType.Eof, "Expected end of expression")
        return expr

    # program -> statement* EOF
    # Syntax errors are recorded in self.errors; the parser then
    # synchronizes and keeps going with the next statement.
    def parse_program(self):
        statements = []
        while not self.is_at_end():
            try:
                statements.append(self.statement())
            except ParseError as e:
                self.errors.append(e)
                self.synchronize()
        return statements

    # --- statements ---

    # statement -> exprStmt | printStmt
    def statement(self):
        if self.match('PRINT'):
            return self.print_statement()
        return self.expression_statement()

    # printStmt -> "print" expression ";"
    def print_statement(self):
        expr = self.expression()
        self.consume('SEMICOLON', "Expected ';' after value")
        return Statement(Statement.Type.PRINT, expr)

    # exprStmt -> expression ";"
    def expression_statement(self):
        expr = self.expression()
        self.consume('SEMICOLON', "Expected ';' after expression")
        return Statement(Statement.Type.EXPRESSION, expr)

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

    # --- error recovery ---

    # Panic mode: discard tokens until we reach a likely statement boundary
    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == 'SEMICOLON':
                return
            if self.peek().type in ('CLASS', 'FUN', 'VAR', 'FOR', 'IF',
                                    'WHILE', 'PRINT', 'RETURN'):
                return
            self.advance()

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
