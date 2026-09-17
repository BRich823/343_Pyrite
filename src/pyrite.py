import sys


def main():
	args = sys.argv[1:]

	if len(args) == 0:
		print("entering REPL")
		while True:
			try:
				_ = input()
			except EOFError:
				break
			print("Scanner Not Implemented")

	elif len(args) == 1:
		# print the contents of the provided file
		try:
			with open(args[0], "r", encoding="utf-8") as f:
				# print file contents without adding extra text
				print(f.read(), end="")
		except FileNotFoundError:
			print(f"File not found: {args[0]}")
			sys.exit(1)

	else:
		# two or more arguments -> not supported
		print("Unexpected number of arguments")
		sys.exit(2)


if __name__ == "__main__":
	main()

