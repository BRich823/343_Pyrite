from enum import Enum

# program       -> statement* EOF 
# statement     -> exprStmt | printStmt
# exprStmt      -> expression ";"
# printStmt     -> "print" expression ";"

class Statement:
    class Type(Enum):
        EXPRESSION = 0
        PRINT = 1
        
    def __init__(self, statement_type, content):
        self.statement_type = statement_type
        self.content = content

    def __repr__(self):
        return f"Statement(type={self.statement_type}, content={self.content})" 