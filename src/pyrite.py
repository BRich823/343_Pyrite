import sys
from scanner import Scanner, ScannerError
from parser import Parser
from ast import ASTPrinter
from evaluator import Statement
from checker import Checker
from variables import TypeCheckError

_printer = ASTPrinter()


def format_statement(stmt):
    if stmt.statement_type == Statement.Type.BLOCK:
        return " ".join(["(block"] + [format_statement(s) for s in stmt.content]) + ")"
    if stmt.statement_type == Statement.Type.DECLARATION:
        var = stmt.content
        annotation = f": {var.type}" if var.annotation or var.strict else ""
        init = f" {_printer.print(var.initializer)}" if var.initializer else ""
        return f"({var.keyword} {var.name}{annotation}{init})"
    kind = 'print' if stmt.statement_type == Statement.Type.PRINT else 'expr'
    return f"({kind} {_printer.print(stmt.content)})"


# checker is passed in by the REPL so declarations persist between lines
def run(source, checker=None):
    s = Scanner(source)
    try:
        s.scan()
    except ScannerError as e:
        print(f"Scan error: {e}")
        return

    parser = Parser(s.tokens)
    statements = parser.parse_program()
    if parser.errors:
        for e in parser.errors:
            print(f"Parse error: {e}")
        return

    checker = checker or Checker()
    checker.errors = []
    checker.check(statements)
    if checker.errors:
        for e in checker.errors:
            kind = 'Type' if isinstance(e, TypeCheckError) else 'Variable'
            print(f"{kind} error: {e}")
        return

    for stmt in statements:
        print(format_statement(stmt))


def main():
    args = sys.argv[1:]

    if len(args) == 0:
        print("entering REPL")
        checker = Checker()
        try:
            while True:
                line = input(">>> ")
                if line.strip():
                    run(line, checker)
        except (KeyboardInterrupt, EOFError):
            print()

    elif len(args) == 1:
        try:
            with open(args[0], 'r') as f:
                run(f.read())
        except OSError as e:
            print(e)

    else:
        print("Usage: python src/pyrite.py or python src/pyrite.py [file]")


if __name__ == "__main__":
    main()
