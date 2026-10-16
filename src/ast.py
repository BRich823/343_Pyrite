from token import *

"""
expression → literal
           | unary
           | binary
           | group;
           
literal    → INT | FLOAT | STRING | "true" | "false" | "null" ;

grouping   → "(" expression ")" ;

unary      → ( "-" | "!" ) expression ;

binary     → expression operator expression ;

operator   → "==" | "!=" | "<" | "<=" | ">" | ">="
            | "+" | "-" | "*" | "/" ; 
"""

class Expression:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)
        
class Binary(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        
    def __str__(self):
        return f"({self.op} {self.left} {self.right})"
        
class Unary(Expression):
    def __init__(self, op, right):
        self.op = op
        self.right = right
        
    def __str__(self):
        return f"({self.op} {self.right})"
        
class Grouping(Expression):
    def __init__(self, exp):
        self.exp = exp

    def __str__(self):
        return f"(group {self.exp})"
    
class Literal(Expression):
    def __init__(self, value):
        self.value = value # NUMBER | STRING | "true" | "false" | "null"
    
    def __str__(self):
        return str(self.value)
    
class ASTPrinter:
    def print(self, expr):
        return self._visit(expr)

    def _visit(self, expr):
        if isinstance(expr, Binary):
            return f"({expr.op} {self._visit(expr.left)} {self._visit(expr.right)})"
        if isinstance(expr, Unary):
            return f"({expr.op} {self._visit(expr.right)})"
        if isinstance(expr, Grouping):
            return f"(group {self._visit(expr.exp)})"
        if isinstance(expr, Literal):
            return str(expr.value)
        raise ValueError(f"Unknown expression type: {type(expr).__name__}")


if __name__ == "__main__":
    exp = Binary(
        Unary(Punctuator('-', 1), Literal(123)),
        Punctuator('*', 1),
        Grouping(Literal(45.67))
    )
    print(exp)