from enum import Enum

# program       -> declaration* EOF
# declaration   -> varDecl | letDecl | constDecl | statement   (see variables.py)
# statement     -> exprStmt | printStmt | block
# block         -> "{" declaration* "}"
# exprStmt      -> expression ";"
# printStmt     -> "print" expression ";"

class Statement:
    class Type(Enum):
        EXPRESSION = 0
        PRINT = 1
        DECLARATION = 2
        BLOCK = 3
        
    def __init__(self, statement_type, content):
        self.statement_type = statement_type
        self.content = content

    def __repr__(self):
        return f"Statement(type={self.statement_type}, content={self.content})" 