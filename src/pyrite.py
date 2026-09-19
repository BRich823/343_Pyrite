import sys


def main():
	args = sys.argv[1:]

	if len(args) == 0:
		print("entering REPL")
		while True:
			try:
				_ = input()
			except KeyboardInterrupt:
				print("Exiting REPL")
				break
			print("Scanner Not Implemented")

	elif len(args) == 1:
		print("Scanner Not Implemented")
		with open(args[0]) as f:
			print(f.read())
	else:
		print("Usage: python src/pyrite.py or python src/pyrite.py [file]")


if __name__ == "__main__":
	main()

