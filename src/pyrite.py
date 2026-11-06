import sys
from scanner import Scanner, ScannerError
from parser import Parser
from ast import ASTPrinter
from evaluator import Statement

_printer = ASTPrinter()


def run(source):
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

    for stmt in statements:
        kind = 'print' if stmt.statement_type == Statement.Type.PRINT else 'expr'
        print(f"({kind} {_printer.print(stmt.content)})")


def main():
    args = sys.argv[1:]

    if len(args) == 0:
        print("entering REPL")
        try:
            while True:
                line = input(">>> ")
                if line.strip():
                    run(line)
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
