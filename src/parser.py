from token import TokenType
from ast import Binary, Unary, Grouping, Literal, VarAccess, Assign
from evaluator import Statement
from variables import Variable, Let, Constant, TYPES


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

    # program -> declaration* EOF
    # Syntax errors are recorded in self.errors; the parser then
    # synchronizes and keeps going with the next statement.
    def parse_program(self):
        statements = []
        while not self.is_at_end():
            # a '}' here has no matching '{', report it and skip just that token
            if self.check('RBRACE'):
                self.errors.append(ParseError("Unmatched '}'", self.advance()))
                continue
            self.try_declaration(statements)
        return statements

    # Parses one declaration into statements, recovering on a syntax error
    def try_declaration(self, statements):
        try:
            statements.append(self.declaration())
        except ParseError as e:
            self.errors.append(e)
            self.synchronize()

    # --- statements ---

    # declaration -> varDecl | letDecl | constDecl | statement
    def declaration(self):
        if self.match('VAR'):
            return self.variable_declaration(Variable)
        if self.match('LET'):
            return self.variable_declaration(Let)
        if self.match('CONST'):
            return self.variable_declaration(Constant)
        return self.statement()

    # varDecl   -> "var" IDENTIFIER ( ":" type )? ( "=" expression )? ";"
    # letDecl   -> "let" IDENTIFIER ( ":" type )? ( "=" expression )? ";"
    # constDecl -> "const" IDENTIFIER ( ":" type )? "=" expression ";"
    def variable_declaration(self, cls):
        name = self.consume(TokenType.Identifier, f"Expected variable name after '{cls.keyword}'")
        annotation = None
        if self.match('COLON'):
            annotation = self.type_annotation()
        initializer = None
        if self.match('EQUAL'):
            initializer = self.expression()
        elif cls is Constant:
            raise ParseError("Expected '=' after constant name, constants must be initialized", self.peek())
        self.consume('SEMICOLON', f"Expected ';' after {cls.keyword} declaration")
        return Statement(Statement.Type.DECLARATION, cls(name, initializer, annotation))

    # type -> "number" | "string" | "boolean" | "nil" | "any"
    def type_annotation(self):
        if self.match('NULL'):
            return self.previous()
        token = self.consume(TokenType.Identifier, "Expected type after ':'")
        if token.lex not in TYPES:
            raise ParseError(f"Unknown type '{token.lex}'", token)
        return token

    # statement -> exprStmt | printStmt | block
    def statement(self):
        if self.match('PRINT'):
            return self.print_statement()
        if self.match('LBRACE'):
            return self.block()
        return self.expression_statement()

    # block -> "{" declaration* "}"
    def block(self):
        opening = self.previous()
        statements = []
        while not self.check('RBRACE') and not self.is_at_end():
            self.try_declaration(statements)
        if self.is_at_end():
            raise ParseError("Unmatched '{', expected '}' to close block", opening)
        self.advance()
        return Statement(Statement.Type.BLOCK, statements)

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
        return self.assignment()

    # assignment -> IDENTIFIER "=" assignment | equality
    # Right associative, so a = b = 1 parses as a = (b = 1)
    def assignment(self):
        expr = self.equality()
        if self.match('EQUAL'):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, VarAccess):
                return Assign(expr.name, value)
            # record without throwing, the parser isn't confused about where it is
            self.errors.append(ParseError("Invalid assignment target", equals))
        return expr

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

        if self.match(TokenType.Identifier):
            return VarAccess(self.previous())

        if self.match('LPAREN'):
            expr = self.expression()
            self.consume('RPAREN', "Expected ')' after expression")
            return Grouping(expr)

        raise ParseError("Expected expression", self.peek())

    # --- error recovery ---

    # Panic mode: discard tokens until we reach a likely statement boundary
    # A '}' is never skipped, so an error inside a block can't swallow its closing brace
    def synchronize(self):
        while not self.is_at_end():
            if self.check('RBRACE'):
                return
            self.advance()
            if self.previous().type == 'SEMICOLON':
                return
            if self.peek().type in ('CLASS', 'FUN', 'VAR', 'LET', 'CONST', 'FOR', 'IF',
                                    'WHILE', 'PRINT', 'RETURN', 'LBRACE'):
                return

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
