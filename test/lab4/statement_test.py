import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def load_module(module_name, file_name):
    file_path = SRC / file_name
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Register project modules so internal imports resolve to src/, not stdlib
token_mod = load_module("token", "token.py")
sys.modules["token"] = token_mod

ast_mod = load_module("ast", "ast.py")
sys.modules["ast"] = ast_mod

evaluator_mod = load_module("evaluator", "evaluator.py")
sys.modules["evaluator"] = evaluator_mod

scanner_mod = load_module("pyrite_scanner", "scanner.py")
parser_mod  = load_module("pyrite_parser",  "parser.py")

Scanner    = scanner_mod.Scanner
ParseError = parser_mod.ParseError
Statement  = evaluator_mod.Statement


def parse_program(src):
    s = Scanner(src)
    s.scan()
    parser = parser_mod.Parser(s.tokens)
    statements = parser.parse_program()
    return statements, parser.errors


class StatementTests(unittest.TestCase):
    def test_invalid_statements(self):
        # Panic mode: the parser records each error, synchronizes, and keeps
        # going, so both bad statements are reported in a single pass
        src = '"one"\ntrue;\nprint 2 +'
        statements, errors = parse_program(src)
        self.assertEqual(statements, [])
        self.assertEqual(len(errors), 2)
        self.assertTrue(all(isinstance(e, ParseError) for e in errors))
        self.assertEqual(errors[0].message, "Expected ';' after expression")
        self.assertEqual(errors[1].message, "Expected expression")

    def test_valid_statements(self):
        src = '4 + 2;\nprint "one";\nprint true;\nprint 1 + 2;\nprint nil;'
        expected = [
            (Statement.Type.EXPRESSION, "(+ 4 2)"),
            (Statement.Type.PRINT, '"one"'),
            (Statement.Type.PRINT, "True"),
            (Statement.Type.PRINT, "(+ 1 2)"),
            (Statement.Type.PRINT, "None"),
        ]
        statements, errors = parse_program(src)
        self.assertEqual(errors, [])
        actual = [(s.statement_type, str(s.content)) for s in statements]
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
