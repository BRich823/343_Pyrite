import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
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
import ast as std_ast, token as std_token
token_mod = load_module("token", "token.py")
sys.modules["token"] = token_mod

ast_mod = load_module("ast", "ast.py")
sys.modules["ast"] = ast_mod

evaluator_mod = load_module("evaluator", "evaluator.py")
sys.modules["evaluator"] = evaluator_mod

variables_mod = load_module("variables", "variables.py")
sys.modules["variables"] = variables_mod

scanner_mod = load_module("scanner", "scanner.py")
sys.modules["scanner"] = scanner_mod

parser_mod = load_module("parser", "parser.py")
sys.modules["parser"] = parser_mod

checker_mod = load_module("checker", "checker.py")
sys.modules["checker"] = checker_mod

pyrite_mod = load_module("pyrite", "pyrite.py")

# Put the stdlib modules back so unittest's traceback formatting still works
sys.modules["ast"] = std_ast
sys.modules["token"] = std_token

Scanner        = scanner_mod.Scanner
Checker        = checker_mod.Checker
Environment    = variables_mod.Environment
Variable       = variables_mod.Variable
Let            = variables_mod.Let
Constant       = variables_mod.Constant
VariableError  = variables_mod.VariableError
TypeCheckError = variables_mod.TypeCheckError
Statement      = evaluator_mod.Statement


# Runs a program through pyrite.run and returns its printed lines
def run(src, checker=None):
    out = io.StringIO()
    with redirect_stdout(out):
        pyrite_mod.run(src, checker)
    return out.getvalue().splitlines()


# Makes an IDENTIFIER token by scanning the name
def ident(name):
    s = Scanner(name)
    s.scan()
    return s.tokens[0]


class PyriteTestCase(unittest.TestCase):
    def assertOutput(self, src, expected):
        self.assertEqual(run(src), expected)


# ==============================
# Variable features
# ==============================

class DeclarationTests(PyriteTestCase):
    def test_var_without_initializer(self):
        self.assertOutput("var a;", ["(var a)"])

    def test_var_with_initializer(self):
        self.assertOutput("var b = 1;", ["(var b 1)"])

    def test_var_with_annotation(self):
        self.assertOutput('var s: string = "hi";', ['(var s: string "hi")'])

    def test_var_annotated_without_initializer(self):
        self.assertOutput("var n: number;", ["(var n: number)"])

    def test_let_inferred(self):
        self.assertOutput("let n = 2.5;", ["(let n: number 2.5)"])

    def test_let_annotated(self):
        self.assertOutput("let flag: boolean = true;", ["(let flag: boolean True)"])

    def test_let_annotated_without_initializer(self):
        self.assertOutput("let s: string;", ["(let s: string)"])

    def test_const_inferred(self):
        self.assertOutput("const PI = 3.14;", ["(const PI: number 3.14)"])

    def test_const_annotated(self):
        self.assertOutput('const name: string = "pyrite";', ['(const name: string "pyrite")'])

    def test_any_annotation(self):
        self.assertOutput("var x: any = nil;", ["(var x: any None)"])

    def test_nil_annotation(self):
        self.assertOutput("let x: nil = nil;", ["(let x: nil None)"])

    def test_report_example(self):
        src = ('var a;\nvar b = 1;\nvar s: string = "hi";\nlet n = 2.5;\n'
               'let flag: boolean = true;\nconst PI = 3.14;\n'
               'const name: string = "pyrite";\nvar x: any = nil;')
        self.assertOutput(src, [
            "(var a)",
            "(var b 1)",
            '(var s: string "hi")',
            "(let n: number 2.5)",
            "(let flag: boolean True)",
            "(const PI: number 3.14)",
            '(const name: string "pyrite")',
            "(var x: any None)",
        ])


class AccessTests(PyriteTestCase):
    def test_print_variable(self):
        self.assertOutput("var a = 1;\nprint a;", ["(var a 1)", "(print a)"])

    def test_variable_in_expression(self):
        self.assertOutput("let a = 1;\nprint a * 2;", ["(let a: number 1)", "(print (* a 2))"])

    def test_inferred_any_from_var(self):
        # an untyped var is any, and any + number is any
        self.assertOutput("var a = 1;\nlet b = a + 2;", ["(var a 1)", "(let b: any (+ a 2))"])

    def test_inferred_string_concat(self):
        self.assertOutput('const g = "hi " + "there";', ['(const g: string (+ "hi " "there"))'])

    def test_inferred_comparison_is_boolean(self):
        self.assertOutput("let a = 1;\nlet b = a < 2;", ["(let a: number 1)", "(let b: boolean (< a 2))"])

    def test_report_example(self):
        src = ('var a = 1;\nlet b = a + 2;\nprint a;\nprint b * 2;\n'
               'const greeting = "hi " + "there";\nprint greeting;')
        self.assertOutput(src, [
            "(var a 1)",
            "(let b: any (+ a 2))",
            "(print a)",
            "(print (* b 2))",
            '(const greeting: string (+ "hi " "there"))',
            "(print greeting)",
        ])


class AssignmentTests(PyriteTestCase):
    def test_assign_var(self):
        self.assertOutput("var a = 1;\na = 5;", ["(var a 1)", "(expr (= a 5))"])

    def test_assign_let_same_type(self):
        self.assertOutput("let b = 2;\nb = 3;", ["(let b: number 2)", "(expr (= b 3))"])

    def test_assign_is_right_associative(self):
        self.assertOutput("var a = 1;\nlet b = 2;\na = b = 10;",
                          ["(var a 1)", "(let b: number 2)", "(expr (= a (= b 10)))"])

    def test_any_accepts_other_types(self):
        self.assertOutput('var c: any = 1;\nc = "now a string";',
                          ["(var c: any 1)", '(expr (= c "now a string"))'])

    def test_untyped_var_accepts_other_types(self):
        self.assertOutput('var c = 1;\nc = true;', ["(var c 1)", "(expr (= c True))"])

    def test_assign_in_print(self):
        self.assertOutput("var a;\nprint a = 3;", ["(var a)", "(print (= a 3))"])

    def test_report_example(self):
        src = ('var a = 1;\nlet b = 2;\na = 5;\nb = a + 1;\na = b = 10;\n'
               'var c: any = 1;\nc = "now a string";\nprint a;')
        self.assertOutput(src, [
            "(var a 1)",
            "(let b: number 2)",
            "(expr (= a 5))",
            "(expr (= b (+ a 1)))",
            "(expr (= a (= b 10)))",
            "(var c: any 1)",
            '(expr (= c "now a string"))',
            "(print a)",
        ])


class BlockTests(PyriteTestCase):
    def test_empty_block(self):
        self.assertOutput("{}", ["(block)"])

    def test_block_uses_outer_variable(self):
        self.assertOutput("var a = 1;\n{\nprint a;\n}", ["(var a 1)", "(block (print a))"])

    def test_assign_outer_from_block(self):
        self.assertOutput("var a = 1;\n{\na = 2;\n}", ["(var a 1)", "(block (expr (= a 2)))"])

    def test_shadowing_allowed(self):
        self.assertOutput("var a = 1;\n{\nvar a = 2;\n}", ["(var a 1)", "(block (var a 2))"])

    def test_shadowing_constant_allowed(self):
        self.assertOutput("const a = 1;\n{\nlet a = 2;\na = 3;\n}",
                          ["(const a: number 1)", "(block (let a: number 2) (expr (= a 3)))"])

    def test_shadow_with_different_type(self):
        self.assertOutput('let a = 1;\n{\nlet a = "s";\n}',
                          ["(let a: number 1)", '(block (let a: string "s"))'])

    def test_sibling_blocks_reuse_name(self):
        self.assertOutput("{\nvar a = 1;\n}\n{\nvar a = 2;\n}",
                          ["(block (var a 1))", "(block (var a 2))"])


class ReplTests(unittest.TestCase):
    def test_declarations_persist(self):
        checker = Checker()
        self.assertEqual(run("var a = 1;", checker), ["(var a 1)"])
        self.assertEqual(run("print a;", checker), ["(print a)"])

    def test_errors_persist(self):
        checker = Checker()
        run("const C = 1;", checker)
        self.assertEqual(run("C = 2;", checker),
                         ["Variable error: Cannot assign to 'C' because it is a constant at line 1, column 1"])

    def test_error_line_does_not_block_next_line(self):
        checker = Checker()
        run("print y;", checker)
        self.assertEqual(run("var y = 1;", checker), ["(var y 1)"])


# ==============================
# Environment / Variable classes
# START AI CODE
# ==============================

class EnvironmentTests(unittest.TestCase):
    def test_declare_and_get(self):
        env = Environment()
        env.declare(Variable(ident("a")), 1)
        self.assertEqual(env.get(ident("a")), 1)

    def test_declare_without_value_is_nil(self):
        env = Environment()
        env.declare(Variable(ident("a")))
        self.assertIsNone(env.get(ident("a")))

    def test_assign(self):
        env = Environment()
        env.declare(Variable(ident("a")), 1)
        self.assertEqual(env.assign(ident("a"), 2), 2)
        self.assertEqual(env.get(ident("a")), 2)

    def test_get_undefined(self):
        with self.assertRaises(VariableError) as cm:
            Environment().get(ident("x"))
        self.assertEqual(cm.exception.message, "Undefined variable 'x'")

    def test_assign_undefined(self):
        with self.assertRaises(VariableError):
            Environment().assign(ident("x"), 1)

    def test_redeclare_same_scope(self):
        env = Environment()
        env.declare(Variable(ident("a")))
        with self.assertRaises(VariableError) as cm:
            env.declare(Variable(ident("a")))
        self.assertEqual(cm.exception.message, "'a' is already declared in this scope")

    def test_lookup_walks_outward(self):
        outer = Environment()
        outer.declare(Variable(ident("a")), "outer")
        inner = Environment(Environment(outer))
        self.assertEqual(inner.get(ident("a")), "outer")

    def test_shadowing(self):
        outer = Environment()
        outer.declare(Variable(ident("a")), "outer")
        inner = Environment(outer)
        inner.declare(Variable(ident("a")), "inner")
        self.assertEqual(inner.get(ident("a")), "inner")
        self.assertEqual(outer.get(ident("a")), "outer")

    def test_assign_from_inner_updates_outer(self):
        outer = Environment()
        outer.declare(Variable(ident("a")), 1)
        inner = Environment(outer)
        inner.assign(ident("a"), 2)
        self.assertEqual(outer.get(ident("a")), 2)

    def test_inner_not_visible_from_outer(self):
        outer = Environment()
        inner = Environment(outer)
        inner.declare(Variable(ident("a")), 1)
        with self.assertRaises(VariableError):
            outer.get(ident("a"))

    def test_constant_gets_value_at_declaration(self):
        env = Environment()
        env.declare(Constant(ident("PI")), 3.14)
        self.assertEqual(env.get(ident("PI")), 3.14)

    def test_constant_cannot_be_assigned(self):
        env = Environment()
        env.declare(Constant(ident("PI")), 3.14)
        with self.assertRaises(VariableError) as cm:
            env.assign(ident("PI"), 3)
        self.assertEqual(cm.exception.message, "Cannot assign to 'PI' because it is a constant")
        self.assertEqual(env.get(ident("PI")), 3.14)


class VariableTypeTests(unittest.TestCase):
    def test_var_defaults_to_any(self):
        v = Variable(ident("a"))
        v.resolve_type("number")
        self.assertEqual(v.type, "any")

    def test_let_infers_type(self):
        v = Let(ident("a"))
        v.resolve_type("string")
        self.assertEqual(v.type, "string")

    def test_let_needs_annotation_or_initializer(self):
        with self.assertRaises(TypeCheckError):
            Let(ident("a")).resolve_type(None)

    def test_annotation_wins(self):
        v = Variable(ident("a"), annotation=ident("number"))
        v.resolve_type("number")
        self.assertEqual(v.type, "number")

    def test_annotation_mismatch(self):
        v = Let(ident("a"), annotation=ident("number"))
        with self.assertRaises(TypeCheckError):
            v.resolve_type("string")

    def test_type_of(self):
        type_of = variables_mod.type_of
        self.assertEqual(type_of(True), "boolean")
        self.assertEqual(type_of(1), "number")
        self.assertEqual(type_of(1.5), "number")
        self.assertEqual(type_of("s"), "string")
        self.assertEqual(type_of(None), "nil")

    def test_assignable(self):
        assignable = variables_mod.assignable
        self.assertTrue(assignable("any", "string"))
        self.assertTrue(assignable("number", "any"))
        self.assertTrue(assignable("number", "number"))
        self.assertFalse(assignable("number", "string"))


# ==============================
# New errors
# ==============================

class ParseErrorTests(PyriteTestCase):
    def test_const_without_initializer(self):
        self.assertOutput("const PI;", [
            "Parse error: Expected '=' after constant name, constants must be initialized at line 1, column 9"])

    def test_missing_variable_name(self):
        self.assertOutput("var = 5;", [
            "Parse error: Expected variable name after 'var' at line 1, column 5"])

    def test_missing_type(self):
        self.assertOutput("var x: = 5;", [
            "Parse error: Expected type after ':' at line 1, column 8"])

    def test_unknown_type(self):
        self.assertOutput("var x: int = 5;", [
            "Parse error: Unknown type 'int' at line 1, column 8"])

    def test_missing_semicolon(self):
        self.assertOutput("var x = 5\nprint x;", [
            "Parse error: Expected ';' after var declaration at line 2, column 1"])

    def test_invalid_assignment_target(self):
        self.assertOutput("var a = 1;\nvar b = 2;\na + b = 3;", [
            "Parse error: Invalid assignment target at line 3, column 7"])

    def test_unmatched_open_brace(self):
        self.assertOutput("{\nvar a = 1;", [
            "Parse error: Unmatched '{', expected '}' to close block at line 1, column 1"])

    def test_unmatched_close_brace(self):
        self.assertOutput("var a = 1;\n}", [
            "Parse error: Unmatched '}' at line 2, column 1"])


class VariableErrorTests(PyriteTestCase):
    def test_undefined_access(self):
        self.assertOutput("print y;", [
            "Variable error: Undefined variable 'y' at line 1, column 7"])

    def test_undefined_assign(self):
        self.assertOutput("z = 3;", [
            "Variable error: Undefined variable 'z' at line 1, column 1"])

    def test_out_of_scope(self):
        self.assertOutput("{\nvar inner = 1;\n}\nprint inner;", [
            "Variable error: Undefined variable 'inner' at line 4, column 7"])

    def test_self_reference(self):
        self.assertOutput("var a = a;", [
            "Variable error: Undefined variable 'a' at line 1, column 9"])

    def test_redeclare(self):
        self.assertOutput("var a = 1;\nvar a = 2;", [
            "Variable error: 'a' is already declared in this scope at line 2, column 5"])

    def test_redeclare_in_block(self):
        self.assertOutput("{\nlet a = 1;\nconst a = 2;\n}", [
            "Variable error: 'a' is already declared in this scope at line 3, column 7"])

    def test_assign_constant(self):
        self.assertOutput("const PI = 3.14;\nPI = 3;", [
            "Variable error: Cannot assign to 'PI' because it is a constant at line 2, column 1"])

    def test_assign_constant_from_block(self):
        self.assertOutput("const PI = 3.14;\n{\nPI = 3;\n}", [
            "Variable error: Cannot assign to 'PI' because it is a constant at line 3, column 1"])


class TypeErrorTests(PyriteTestCase):
    def test_annotation_mismatch(self):
        self.assertOutput('let n: number = "five";', [
            "Type error: Type 'string' is not assignable to type 'number' at line 1, column 5"])

    def test_assign_wrong_type_to_inferred(self):
        self.assertOutput('let n = 5;\nn = "five";', [
            "Type error: Type 'string' is not assignable to type 'number' at line 2, column 1"])

    def test_assign_wrong_type_to_annotated_var(self):
        self.assertOutput('var s: string = "a";\ns = 1;', [
            "Type error: Type 'number' is not assignable to type 'string' at line 2, column 1"])

    def test_let_without_type_or_initializer(self):
        self.assertOutput("let x;", [
            "Type error: 'x' needs a type annotation or an initializer at line 1, column 5"])

    def test_arithmetic_on_string(self):
        self.assertOutput('let s = "a";\nprint s - 1;', [
            "Type error: Operator '-' cannot be applied to type 'string' at line 2, column 9"])

    def test_unary_minus_on_boolean(self):
        self.assertOutput("let t = true;\nprint -t;", [
            "Type error: Operator '-' cannot be applied to type 'boolean' at line 2, column 7"])

    def test_plus_incompatible(self):
        self.assertOutput("print true + 1;", [
            "Type error: Operator '+' cannot be applied to types 'boolean' and 'number' at line 1, column 12"])

    def test_compare_booleans(self):
        self.assertOutput("print true < false;", [
            "Type error: Operator '<' cannot be applied to types 'boolean' and 'boolean' at line 1, column 12"])

    def test_equality_no_overlap(self):
        self.assertOutput('print 1 == "1";', [
            "Type error: This comparison appears to be unintentional because the types "
            "'number' and 'string' have no overlap at line 1, column 9"])


class MultipleErrorTests(PyriteTestCase):
    def test_all_errors_reported(self):
        self.assertOutput("print y;\nconst C = 1;\nC = 2;\nlet n: string = 4;", [
            "Variable error: Undefined variable 'y' at line 1, column 7",
            "Variable error: Cannot assign to 'C' because it is a constant at line 3, column 1",
            "Type error: Type 'number' is not assignable to type 'string' at line 4, column 5",
        ])

    def test_bad_declaration_does_not_cascade(self):
        # n is still declared after its type error, so 'print n' isn't "undefined"
        self.assertOutput('let n: number = "five";\nprint n;', [
            "Type error: Type 'string' is not assignable to type 'number' at line 1, column 5"])


# ==============================
# Scoping example
# ==============================

class ScopingExampleTests(PyriteTestCase):
    SRC = (Path(__file__).parent / "scoping_example.txt").read_text()

    def test_output(self):
        self.assertOutput(self.SRC, [
            '(var a "global a")',
            '(var b "global b")',
            '(var c "global c")',
            '(block (var a "outer a") (var b "outer b") (block (var a "inner a") '
            '(print a) (print b) (print c)) (print a) (print b) (print c))',
            "(print a)",
            "(print b)",
            "(print c)",
        ])

    # Walks the program with real Environments (one per block) and records the
    # value each print resolves to, i.e. what the program will print once
    # evaluation is added
    def test_resolution(self):
        s = Scanner(self.SRC)
        s.scan()
        statements = parser_mod.Parser(s.tokens).parse_program()
        printed = []

        def walk(stmts, env):
            for stmt in stmts:
                if stmt.statement_type == Statement.Type.DECLARATION:
                    env.declare(stmt.content, stmt.content.initializer.value.strip('"'))
                elif stmt.statement_type == Statement.Type.BLOCK:
                    walk(stmt.content, Environment(env))
                elif stmt.statement_type == Statement.Type.PRINT:
                    printed.append(env.get(stmt.content.name))

        walk(statements, Environment())
        self.assertEqual(printed, [
            "inner a", "outer b", "global c",
            "outer a", "outer b", "global c",
            "global a", "global b", "global c",
        ])

    def test_redeclare_in_same_scope_still_errors(self):
        self.assertOutput('var a = "global a";\n{\nvar a = "outer a";\nvar a = "again";\n}', [
            "Variable error: 'a' is already declared in this scope at line 4, column 5"])

# --- END AI CODE ---

if __name__ == "__main__":
    unittest.main()
