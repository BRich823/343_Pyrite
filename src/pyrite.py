import sys
from scanner import Scanner, ScannerError
from parser import Parser, ParseError
from ast import ASTPrinter

_printer = ASTPrinter()


def run(source):
    s = Scanner(source)
    try:
        s.scan()
    except ScannerError as e:
        print(f"Scan error: {e}")
        return

    try:
        ast = Parser(s.tokens).parse()
        print(_printer.print(ast))
    except ParseError as e:
        print(f"Parse error: {e}")


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
