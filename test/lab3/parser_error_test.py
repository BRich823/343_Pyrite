import importlib.util
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


import sys

# Register project modules so internal imports resolve to src/, not stdlib
token_mod = load_module("token", "token.py")
sys.modules["token"] = token_mod

ast_mod = load_module("ast", "ast.py")
sys.modules["ast"] = ast_mod

scanner_mod = load_module("pyrite_scanner", "scanner.py")
parser_mod  = load_module("pyrite_parser",  "parser.py")

Scanner    = scanner_mod.Scanner
ParseError = parser_mod.ParseError


def parse(src):
    s = Scanner(src)
    s.scan()
    return parser_mod.Parser(s.tokens).parse()


def assert_parse_error(test, src):
    with test.assertRaises(ParseError, msg=f"Expected ParseError for: {src!r}"):
        parse(src)
# AI code

class UnmatchedParenTests(unittest.TestCase):
    def test_unclosed_open_paren(self):
        assert_parse_error(self, "(1 + 2")

    def test_extra_close_paren(self):
        assert_parse_error(self, "1 + 2)")

    def test_nested_unclosed(self):
        assert_parse_error(self, "((1 + 2)")

    def test_empty_parens(self):
        assert_parse_error(self, "()")


class MissingOperandTests(unittest.TestCase):
    def test_missing_right_operand_plus(self):
        assert_parse_error(self, "1 +")

    def test_missing_right_operand_minus(self):
        assert_parse_error(self, "1 -")

    def test_missing_right_operand_star(self):
        assert_parse_error(self, "1 *")

    def test_missing_right_operand_slash(self):
        assert_parse_error(self, "1 /")

    def test_missing_right_operand_equality(self):
        assert_parse_error(self, "1 ==")

    def test_missing_right_operand_comparison(self):
        assert_parse_error(self, "1 >=")

    def test_missing_left_operand(self):
        assert_parse_error(self, "* 2")


class UnexpectedTokenTests(unittest.TestCase):
    def test_double_operator(self):
        assert_parse_error(self, "1 ++ 2")

    def test_operator_only(self):
        assert_parse_error(self, "+")

    def test_consecutive_literals(self):
        # two literals with no operator between them — parser consumes
        # the first, then expects EOF but finds the second
        assert_parse_error(self, "1 2")

    def test_bare_equality(self):
        assert_parse_error(self, "== 1")


class SyntaxErrorTests(unittest.TestCase):
    def test_empty_input(self):
        assert_parse_error(self, "")

    def test_unary_without_operand(self):
        assert_parse_error(self, "!")

    def test_unary_minus_without_operand(self):
        assert_parse_error(self, "-")

    def test_deeply_nested_unclosed(self):
        assert_parse_error(self, "(((1 + 2)")
# end AI code

if __name__ == "__main__":
    unittest.main()
