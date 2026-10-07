import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

# ---AI code---
def load_module(module_name, file_name):
    file_path = SRC / file_name
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pyrite_ast = load_module("pyrite_ast", "ast.py")
pyrite_token = load_module("pyrite_token", "token.py")

Binary = pyrite_ast.Binary
Grouping = pyrite_ast.Grouping
Literal = pyrite_ast.Literal
Unary = pyrite_ast.Unary
Punctuator = pyrite_token.Punctuator
# ---end AI code---

class AstExampleTests(unittest.TestCase):
    def test_example_binary_of_unary_and_grouping(self):
        expr = Binary(
            Unary(Punctuator('-', 1), Literal(376)),
            Punctuator('+', 1),
            Grouping(Literal(2.3)),
        )
        self.assertEqual(str(expr), "(+ (- 376) (group 2.3))")

    def test_example_binary_with_same_structure_but_different_numbers(self):
        expr = Binary(
            Unary(Punctuator('-', 1), Literal(7)),
            Punctuator('+', 1),
            Grouping(Literal(3.5)),
        )
        self.assertEqual(str(expr), "(+ (- 7) (group 3.5))")

    def test_example_nested_binary_expression(self):
        expr = Binary(
            Grouping(
                Binary(
                    Literal(2),
                    Punctuator('+', 1),
                    Literal(3),
                )
            ),
            Punctuator('*', 1),
            Unary(Punctuator('-', 1), Literal(4)),
        )
        self.assertEqual(str(expr), "(* (group (+ 2 3)) (- 4))")

    def test_example_unary_then_binary_then_grouping(self):
        expr = Binary(
            Unary(Punctuator('-', 1), Literal(10)),
            Punctuator('*', 1),
            Grouping(
                Binary(
                    Literal(5),
                    Punctuator('-', 1),
                    Literal(2),
                )
            ),
        )
        self.assertEqual(str(expr), "(* (- 10) (group (- 5 2)))")


if __name__ == "__main__":
    unittest.main()
