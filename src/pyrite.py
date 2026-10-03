import sys
from scanner import Scanner, Error

def main():
	args = sys.argv[1:]
	s = Scanner(args[0] if len(args) == 1 else [])
	if len(args) == 0:
		print("entering REPL")
		try:
			while True:
				s.add_line(input(">>> "))
				s.print_tokens()
		except (KeyboardInterrupt, EOFError) as cause:
			try:
				raise Error("REPL terminated", s.get_loc()) from cause
			except Error as e:
				print(e)
		except Error as e:
			print(e)

	elif len(args) == 1:
		try:
			with open(args[0], 'r') as f:
				s.set_source(f.read())
			s.print_tokens()
		except Error as e:
			print(e)
	else:
		print("Usage: python src/pyrite.py or python src/pyrite.py [file]")


if __name__ == "__main__":
	main()

