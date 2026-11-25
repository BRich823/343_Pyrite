"""
declaration   → varDecl | letDecl | constDecl | statement

varDecl       → "var" IDENTIFIER ( ":" type )? ( "=" expression )? ";"

letDecl       → "let" IDENTIFIER ( ":" type )? ( "=" expression )? ";"

constDecl     → "const" IDENTIFIER ( ":" type )? "=" expression ";"

type          → "number" | "string" | "boolean" | "nil" | "any"
"""

NUMBER = 'number'
STRING = 'string'
BOOLEAN = 'boolean'
NIL = 'nil'
ANY = 'any'
TYPES = {NUMBER, STRING, BOOLEAN, NIL, ANY}


# Type of a runtime value (bool is checked first since it's a subclass of int)
def type_of(value):
    if isinstance(value, bool):
        return BOOLEAN
    if isinstance(value, (int, float)):
        return NUMBER
    if isinstance(value, str):
        return STRING
    if value is None:
        return NIL
    return ANY


# 'any' is assignable both ways, otherwise the types must match exactly
def assignable(target, source):
    return target == ANY or source == ANY or target == source


class VariableError(Exception):
    def __init__(self, message, token):
        self.message = message
        self.token = token

    def __str__(self):
        loc = self.token.loc if self.token else None
        if loc:
            return f"{self.message} at line {loc[0] + 1}, column {loc[1] + 1}"
        return self.message


class TypeCheckError(VariableError):
    pass


class Variable:
    keyword = 'var'
    strict = False  # var is untyped (any) unless annotated

    def __init__(self, name, initializer=None, annotation=None):
        self.name = name                # IDENTIFIER token
        self.initializer = initializer  # expression or None
        self.annotation = annotation    # type token or None
        self.type = ANY                 # resolved by the checker
        self.value = None               # runtime value

    # Sets self.type from the annotation, or infers it from the initializer
    def resolve_type(self, initializer_type=None):
        if self.annotation:
            self.type = self.annotation.lex
        elif self.strict and initializer_type:
            self.type = initializer_type
        elif self.strict:
            raise TypeCheckError(
                f"'{self.name.lex}' needs a type annotation or an initializer", self.name)
        else:
            self.type = ANY
        if initializer_type:
            self.check_type(initializer_type, self.name)

    def check_type(self, value_type, token):
        if not assignable(self.type, value_type):
            raise TypeCheckError(
                f"Type '{value_type}' is not assignable to type '{self.type}'", token)

    def check_assignable(self, token):
        pass

    def assign(self, value, token=None):
        self.check_assignable(token)
        self.value = value

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name.lex!r}, type={self.type!r}, initializer={self.initializer})"


class Let(Variable):
    keyword = 'let'
    strict = True


class Constant(Variable):
    keyword = 'const'
    strict = True

    # A constant only gets its value at declaration (Environment.declare)
    def check_assignable(self, token):
        raise VariableError(
            f"Cannot assign to '{self.name.lex}' because it is a constant", token or self.name)


class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing  # parent scope, None for global
        self.variables = {}

    # declaration: binds a name in this scope, shadowing any outer scope
    def declare(self, variable, value=None):
        name = variable.name.lex
        if name in self.variables:
            raise VariableError(f"'{name}' is already declared in this scope", variable.name)
        variable.value = value
        self.variables[name] = variable

    # access: looks up the current value of a name
    def get(self, name):
        return self.lookup(name).value

    # assignment: updates an existing name, constants reject this
    def assign(self, name, value):
        self.lookup(name).assign(value, name)
        return value

    # Walks from the innermost scope outward to find a name
    def lookup(self, name):
        scope = self
        while scope is not None:
            if name.lex in scope.variables:
                return scope.variables[name.lex]
            scope = scope.enclosing
        raise VariableError(f"Undefined variable '{name.lex}'", name)
