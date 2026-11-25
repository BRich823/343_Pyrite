from ast import Binary, Unary, Grouping, Literal, VarAccess, Assign
from evaluator import Statement
from variables import (Environment, VariableError, TypeCheckError, type_of,
                       NUMBER, STRING, BOOLEAN, ANY)


# Static pass over the program (like tsc): resolves every name against its
# block scope and checks types, collecting errors in self.errors
class Checker:
    def __init__(self):
        self.env = Environment()
        self.errors = []

    def check(self, statements):
        for stmt in statements:
            try:
                self.statement(stmt)
            except VariableError as e:
                self.errors.append(e)

    # --- statements ---

    def statement(self, stmt):
        if stmt.statement_type == Statement.Type.DECLARATION:
            self.declaration(stmt.content)
        elif stmt.statement_type == Statement.Type.BLOCK:
            self.block(stmt.content)
        else:
            self.expression(stmt.content)

    # Each block gets a new scope that is thrown away when the block ends
    def block(self, statements):
        previous = self.env
        self.env = Environment(previous)
        try:
            self.check(statements)
        finally:
            self.env = previous

    def declaration(self, variable):
        # Initializer is checked before the name exists, so it can't refer to itself
        try:
            init_type = self.expression(variable.initializer) if variable.initializer else None
            variable.resolve_type(init_type)
        finally:
            # declared even on error so later uses don't cascade into "undefined" errors
            self.env.declare(variable)

    # --- expressions (each returns the expression's type) ---

    def expression(self, expr):
        if isinstance(expr, Literal):
            return type_of(expr.value)
        if isinstance(expr, Grouping):
            return self.expression(expr.exp)
        if isinstance(expr, VarAccess):
            return self.env.lookup(expr.name).type
        if isinstance(expr, Assign):
            return self.assign(expr)
        if isinstance(expr, Unary):
            return self.unary(expr)
        if isinstance(expr, Binary):
            return self.binary(expr)
        raise ValueError(f"Unknown expression type: {type(expr).__name__}")

    def assign(self, expr):
        variable = self.env.lookup(expr.name)
        variable.check_assignable(expr.name)
        value_type = self.expression(expr.value)
        variable.check_type(value_type, expr.name)
        return variable.type

    def unary(self, expr):
        right = self.expression(expr.right)
        if expr.op.type == 'BANG':
            return BOOLEAN
        self.expect_number(expr.op, right)
        return NUMBER

    def binary(self, expr):
        left = self.expression(expr.left)
        right = self.expression(expr.right)
        op = expr.op

        if op.type == 'PLUS':
            if STRING in (left, right):
                return STRING
            if ANY in (left, right):
                return ANY
            if left == right == NUMBER:
                return NUMBER
            raise self.operator_error(op, left, right)

        if op.type in ('MINUS', 'STAR', 'SLASH'):
            self.expect_number(op, left, right)
            return NUMBER

        if op.type in ('GREATER', 'GREATER_EQUAL', 'LESS', 'LESS_EQUAL'):
            if ANY in (left, right) or left == right and left in (NUMBER, STRING):
                return BOOLEAN
            raise self.operator_error(op, left, right)

        # == and != : comparing two unrelated types is always a mistake
        if ANY not in (left, right) and left != right:
            raise TypeCheckError(
                f"This comparison appears to be unintentional because the types "
                f"'{left}' and '{right}' have no overlap", op)
        return BOOLEAN

    # --- helpers ---

    def expect_number(self, op, *types):
        for t in types:
            if t not in (NUMBER, ANY):
                raise TypeCheckError(f"Operator '{op.lex}' cannot be applied to type '{t}'", op)

    def operator_error(self, op, left, right):
        return TypeCheckError(
            f"Operator '{op.lex}' cannot be applied to types '{left}' and '{right}'", op)
