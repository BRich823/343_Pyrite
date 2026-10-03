## start AI code
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYRITE = ROOT / "src" / "pyrite.py"


def scan_token_types(source):
	"""Run the scanner CLI and return the emitted token type names."""
	with tempfile.TemporaryDirectory() as directory:
		source_path = Path(directory) / "scanner-input.pyr"
		source_path.write_text(source + "\n", encoding="utf-8")
		result = subprocess.run(
			[sys.executable, str(PYRITE), str(source_path)],
			cwd=ROOT,
			capture_output=True,
			text=True,
			check=False,
		)

	if result.returncode != 0:
		raise AssertionError(
			f"Scanner exited with {result.returncode}:\n{result.stderr}"
		)

	return re.findall(r"^Token\(([^,]+),", result.stdout, re.MULTILINE)


def scan_error(source):
	script = (
		"from scanner import Scanner, ScannerError\n"
		"try:\n"
		f"\tScanner({source!r}).scan()\n"
		"except ScannerError as error:\n"
		"\tprint(type(error).__name__)\n"
		"\tprint(error)\n"
		"else:\n"
		"\traise SystemExit('ScannerError was not raised')\n"
	)
	return subprocess.run(
		[sys.executable, "-c", script],
		cwd=ROOT / "src",
		capture_output=True,
		text=True,
		check=False,
	)


class ScannerTokenTests(unittest.TestCase):
	def assert_single_token(self, source, expected_type):
		self.assertEqual(scan_token_types(source), [expected_type, "EOL", "EOF"])

	def test_every_keyword_token(self):
		keywords = {
			"and": "AND",
			"class": "CLASS",
			"else": "ELSE",
			"false": "FALSE",
			"for": "FOR",
			"fun": "FUN",
			"if": "IF",
			"nil": "NULL",
			"or": "OR",
			"print": "PRINT",
			"return": "RETURN",
			"super": "SUPER",
			"this": "THIS",
			"true": "TRUE",
			"var": "VAR",
			"while": "WHILE",
		}
		for lexeme, token_type in keywords.items():
			with self.subTest(keyword=lexeme):
				self.assert_single_token(lexeme, token_type)

	def test_identifier_start_and_continuation_rules(self):
		for lexeme in ("name", "_hidden", "item7", "camelCase", "a_b_2"):
			with self.subTest(identifier=lexeme):
				self.assert_single_token(lexeme, "IDENTIFIER")

	def test_keyword_prefix_is_an_identifier(self):
		for lexeme in ("variable", "printable", "while2"):
			with self.subTest(identifier=lexeme):
				self.assert_single_token(lexeme, "IDENTIFIER")

	def test_integer_literals(self):
		for lexeme in ("0", "7", "2048"):
			with self.subTest(literal=lexeme):
				self.assert_single_token(lexeme, "INT")

	def test_float_literals(self):
		for lexeme in ("0.5", "3.14", "10.0"):
			with self.subTest(literal=lexeme):
				self.assert_single_token(lexeme, "FLOAT")

	def test_quoted_string_literals(self):
		for lexeme in ('"hello"', "'world'"):
			with self.subTest(literal=lexeme):
				self.assert_single_token(lexeme, "STR")

	def test_literal_at_end_of_line(self):
		self.assert_single_token("42", "INT")

	def test_every_punctuator_token(self):
		punctuators = {
			"(": "LPAREN",
			")": "RPAREN",
			"[": "LBRACK",
			"]": "RBRACK",
			"{": "LBRACE",
			"}": "RBRACE",
			",": "COMMA",
			":": "COLON",
			";": "SEMICOLON",
			".": "DOT",
			"+": "PLUS",
			"-": "MINUS",
			"*": "STAR",
			"!": "BANG",
			"!=": "BANG_EQUAL",
			"=": "EQUAL",
			"==": "EQUAL_EQUAL",
			">": "GREATER",
			">=": "GREATER_EQUAL",
			"<": "LESS",
			"<=": "LESS_EQUAL",
			"/": "SLASH",
			"//": "SLASH_SLASH",
		}
		for lexeme, token_type in punctuators.items():
			with self.subTest(punctuator=lexeme):
				self.assert_single_token(lexeme, token_type)

	def test_tokens_are_separated_by_whitespace(self):
		self.assertEqual(
			scan_token_types("var total = 12"),
			["VAR", "IDENTIFIER", "EQUAL", "INT", "EOL", "EOF"],
		)

	def test_each_source_line_ends_with_eol(self):
		self.assertEqual(
			scan_token_types("first\nsecond"),
			["IDENTIFIER", "EOL", "IDENTIFIER", "EOL", "EOF"],
		)
# end AI code (lots of this was tweaked heavily)

class ScannerErrorTests(unittest.TestCase):
	def assert_scanner_error(self, source, expected_message):
		result = scan_error(source)
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertEqual(
			result.stdout.splitlines(),
			["ScannerError", expected_message],
		)

	def test_unexpected_character_raises_located_error(self):
		self.assert_scanner_error(
			["var value", "  @"],
			"Unexpected character '@' at line 2, column 3",
		)

	def test_unterminated_string_raises_located_error(self):
		self.assert_scanner_error(
			["print", "  'unfinished"],
			"Unterminated string at line 2, column 3",
		)

	def test_repl_eof_prints_termination_error(self):
		result = subprocess.run(
			[sys.executable, str(PYRITE)],
			cwd=ROOT,
			input="",
			capture_output=True,
			text=True,
			check=False,
		)
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertIn("REPL terminated at line 1, column 1", result.stdout)
		self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
	unittest.main()
